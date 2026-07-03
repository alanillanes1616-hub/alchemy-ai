"""
embeddings.py — Wrapper sobre GoogleGenerativeAIEmbeddings.

Centraliza la creación del modelo de embeddings para que el resto
del sistema lo consuma sin acoplarse a la implementación concreta.
"""

import streamlit as st
from langchain_google_genai import GoogleGenerativeAIEmbeddings

from config import EMBEDDING_MODEL
from utils import get_logger

logger = get_logger("embeddings")


@st.cache_resource(show_spinner=False)
def get_embedding_model(api_key: str) -> GoogleGenerativeAIEmbeddings:
    """
    Retorna el modelo de embeddings cacheado por Streamlit.

    Args:
        api_key: Google API key.

    Returns:
        Instancia de GoogleGenerativeAIEmbeddings lista para usar.
    """
    logger.info("Loading embedding model: %s", EMBEDDING_MODEL)
    return GoogleGenerativeAIEmbeddings(
        model=EMBEDDING_MODEL,
        google_api_key=api_key,
    )
