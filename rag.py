"""
rag.py — Pipeline RAG completo: chunking, indexación FAISS y recuperación semántica.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document

from config import CHUNK_SIZE, CHUNK_OVERLAP, RETRIEVAL_K
from embeddings import get_embedding_model
from utils import get_logger

logger = get_logger("rag")


# ── Modelos de datos ──────────────────────────────────────────────────────────

@dataclass
class RetrievedChunk:
    """Fragmento recuperado con metadatos de origen."""
    text: str
    source: str
    page: int
    score: float = 0.0

    def citation(self) -> str:
        return f"[{self.source}, p. {self.page}]"


# ── RAG Engine ────────────────────────────────────────────────────────────────

class RAGEngine:
    """
    Gestiona el índice FAISS y expone búsqueda semántica.

    Uso:
        engine = RAGEngine(api_key)
        engine.index_pages(pages)
        chunks = engine.retrieve("mi consulta")
    """

    def __init__(self, api_key: str) -> None:
        self._embeddings = get_embedding_model(api_key)
        self._vectorstore: Optional[FAISS] = None
        self._splitter = RecursiveCharacterTextSplitter(
            chunk_size=CHUNK_SIZE,
            chunk_overlap=CHUNK_OVERLAP,
            separators=["\n\n", "\n", ". ", " ", ""],
        )

    # ── Indexación ────────────────────────────────────────────────────────────

    def index_pages(self, pages: list[dict]) -> int:
        """
        Toma las páginas extraídas por documents.py y las indexa en FAISS.

        Args:
            pages: Lista de dicts {"page": int, "text": str, "source": str}.

        Returns:
            Número total de chunks indexados.
        """
        docs: list[Document] = []
        for entry in pages:
            chunks = self._splitter.split_text(entry["text"])
            for chunk in chunks:
                docs.append(Document(
                    page_content=chunk,
                    metadata={"source": entry["source"], "page": entry["page"]},
                ))

        if not docs:
            logger.warning("No chunks generated from provided pages.")
            return 0

        if self._vectorstore is None:
            self._vectorstore = FAISS.from_documents(docs, self._embeddings)
        else:
            self._vectorstore.add_documents(docs)

        logger.info("Indexed %d chunks into FAISS.", len(docs))
        return len(docs)

    def clear(self) -> None:
        """Elimina el índice actual."""
        self._vectorstore = None
        logger.info("FAISS index cleared.")

    def has_index(self) -> bool:
        return self._vectorstore is not None

    # ── Recuperación ──────────────────────────────────────────────────────────

    def retrieve(self, query: str, k: int = RETRIEVAL_K) -> list[RetrievedChunk]:
        """
        Búsqueda semántica por similitud.

        Args:
            query: Consulta del usuario.
            k:     Número de chunks a recuperar.

        Returns:
            Lista de RetrievedChunk ordenados por relevancia descendente.
        """
        if not self._vectorstore:
            return []

        try:
            results = self._vectorstore.similarity_search_with_relevance_scores(query, k=k)
        except Exception as exc:
            logger.error("Retrieval error: %s", exc)
            return []

        chunks = []
        for doc, score in results:
            chunks.append(RetrievedChunk(
                text=doc.page_content,
                source=doc.metadata.get("source", "desconocido"),
                page=doc.metadata.get("page", 0),
                score=score,
            ))

        logger.info("Retrieved %d chunks for query (top score: %.3f).",
                    len(chunks), chunks[0].score if chunks else 0)
        return chunks

    # ── Contexto formateado ───────────────────────────────────────────────────

    def build_context(self, chunks: list[RetrievedChunk]) -> str:
        """Formatea los chunks recuperados como bloque de contexto para el LLM."""
        if not chunks:
            return ""
        sections = []
        for ch in chunks:
            sections.append(f"{ch.citation()}\n{ch.text}")
        return "\n\n---\n\n".join(sections)

