# ---------------- AUTH SIMPLE ----------------

PASSWORD = "1234"  # cámbiala luego

if "auth" not in st.session_state:
    st.session_state.auth = False

if not st.session_state.auth:
    st.title("🔒 Acceso restringido")

    password = st.text_input("Ingresa la contraseña", type="password")

    if password == PASSWORD:
        st.session_state.auth = True
        st.rerun()
    elif password:
        st.error("Contraseña incorrecta")

    st.stop()
"""
app.py — Punto de entrada de Alchemy AI.

Orquesta todos los módulos: UI, LLM, RAG, memoria, documentos y exportación.

Ejecutar:
    streamlit run app.py
"""

import streamlit as st

# ── Page config (debe ser lo primero) ─────────────────────────────────────────
st.set_page_config(
    page_title="Alchemy AI",
    page_icon="◈",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Imports internos ──────────────────────────────────────────────────────────
from config import (
    AVAILABLE_MODELS, DEFAULT_MODEL, DEFAULT_TEMPERATURE,
    DEFAULT_MAX_TOKENS, DEFAULT_TOP_P, DEFAULT_TOP_K,
    MODES, EXPORT_FORMATS, ACCEPTED_EXTENSIONS,
)
from documents import extract_document
from embeddings import get_embedding_model
from export import export
from llm import LLMConfig, build_llm, invoke
from memory import ConversationMemory
from prompts import build_system_prompt
from rag import RAGEngine
from ui import inject_css, render_header, render_chat_history, render_document_list, render_welcome
from utils import file_hash, get_logger

logger = get_logger("app")

# ── CSS ───────────────────────────────────────────────────────────────────────

# ── API Key ───────────────────────────────────────────────────────────────────
GOOGLE_API_KEY: str = st.secrets.get("GOOGLE_API_KEY", "")
if not GOOGLE_API_KEY:
    st.error(
        "GOOGLE_API_KEY no encontrada. "
        "Agrégala en `.streamlit/secrets.toml` como: GOOGLE_API_KEY = 'tu_clave'"
    )
    st.stop()

# ── Session State — inicialización ────────────────────────────────────────────
def _init_state() -> None:
    defaults = {
        "memory":    ConversationMemory(),
        "rag":       RAGEngine(GOOGLE_API_KEY),
        "documents": {},          # {filename: {"pages": int, "chunks": int}}
        "mode":      "Chat",
        "llm_cfg":   LLMConfig(
            model=DEFAULT_MODEL,
            temperature=DEFAULT_TEMPERATURE,
            max_tokens=DEFAULT_MAX_TOKENS,
            top_p=DEFAULT_TOP_P,
            top_k=DEFAULT_TOP_K,
            api_key=GOOGLE_API_KEY,
        ),
    }
    for key, val in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = val

_init_state()

memory: ConversationMemory = st.session_state.memory
rag: RAGEngine             = st.session_state.rag
documents: dict            = st.session_state.documents

# ════════════════════════════════════════════════════════════════════════════
# SIDEBAR
# ════════════════════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("### Alchemy AI")
    st.markdown("---")

    # ── Modo de trabajo ───────────────────────────────────────────────────────
    st.markdown("**Modo de trabajo**")
    selected_mode = st.radio(
        "Modo",
        options=list(MODES.keys()),
        index=list(MODES.keys()).index(st.session_state.mode),
        label_visibility="collapsed",
    )
    if selected_mode != st.session_state.mode:
        st.session_state.mode = selected_mode

    st.caption(MODES[st.session_state.mode])
    st.markdown("---")

    # ── Carga de documentos ───────────────────────────────────────────────────
    st.markdown("**Documentos**")
    uploaded_files = st.file_uploader(
        "Sube archivos",
        type=ACCEPTED_EXTENSIONS,
        accept_multiple_files=True,
        label_visibility="collapsed",
    )

    if uploaded_files:
        for uf in uploaded_files:
            content = uf.read()
            fhash = file_hash(content)
            doc_key = f"{uf.name}_{fhash}"

            if doc_key not in documents:
                with st.spinner(f"Procesando {uf.name}..."):
                    pages = extract_document(content, uf.name)
                    if pages:
                        n_chunks = rag.index_pages(pages)
                        documents[doc_key] = {
                            "display_name": uf.name,
                            "pages": len(pages),
                            "chunks": n_chunks,
                        }
                        logger.info("Indexed: %s (%d chunks)", uf.name, n_chunks)
                        st.success(f"{uf.name} — {n_chunks} chunks indexados")
                    else:
                        st.warning(f"No se pudo extraer texto de {uf.name}")

    # ── Lista de documentos ───────────────────────────────────────────────────
    if documents:
        st.markdown("**Archivos cargados**")
        display_docs = {
            meta["display_name"]: {"pages": meta["pages"], "chunks": meta["chunks"]}
            for meta in documents.values()
        }
        to_remove_names = render_document_list(display_docs)

        if to_remove_names:
            # Eliminar del registro y reconstruir el índice
            keys_to_del = [
                k for k, v in documents.items()
                if v["display_name"] in to_remove_names
            ]
            for k in keys_to_del:
                del documents[k]
            rag.clear()
            st.info("Documento eliminado. El índice ha sido reiniciado.")
            st.rerun()

    st.markdown("---")

    # ── Acciones ──────────────────────────────────────────────────────────────
    st.markdown("**Acciones**")

    if st.button("Nuevo chat"):
        memory.clear()
        st.rerun()

    if not memory.is_empty():
        st.markdown("**Exportar conversación**")
        export_fmt = st.selectbox(
            "Formato",
            EXPORT_FORMATS,
            label_visibility="collapsed",
        )
        if st.button("Exportar"):
            try:
                data, filename, mime = export(memory, export_fmt)
                st.download_button(
                    label=f"Descargar {filename}",
                    data=data,
                    file_name=filename,
                    mime=mime,
                )
            except Exception as exc:
                st.error(f"Error al exportar: {exc}")

    st.markdown("---")

    # ── Configuración del modelo ──────────────────────────────────────────────
    with st.expander("Configuracion del modelo"):
        cfg = st.session_state.llm_cfg

        new_model = st.selectbox("Modelo", AVAILABLE_MODELS,
                                 index=AVAILABLE_MODELS.index(cfg.model))
        new_temp  = st.slider("Temperatura", 0.0, 1.0, cfg.temperature, 0.05)
        new_tok   = st.slider("Max tokens", 256, 16384, cfg.max_tokens, 256)
        new_top_p = st.slider("Top P", 0.0, 1.0, cfg.top_p, 0.05)
        new_top_k = st.slider("Top K", 1, 100, cfg.top_k, 1)

        new_cfg = LLMConfig(
            model=new_model, temperature=new_temp, max_tokens=new_tok,
            top_p=new_top_p, top_k=new_top_k, api_key=GOOGLE_API_KEY,
        )
        if new_cfg != cfg:
            st.session_state.llm_cfg = new_cfg

    st.markdown(
        f"<p style='font-size:10px; color:#9ca3af; margin-top:8px;'>"
        f"Modelo: {st.session_state.llm_cfg.model}</p>",
        unsafe_allow_html=True,
    )

# ════════════════════════════════════════════════════════════════════════════
# ÁREA PRINCIPAL
# ════════════════════════════════════════════════════════════════════════════
render_header(st.session_state.mode)

tab_chat, tab_corpus = st.tabs(["Chat", "Corpus"])

# ── Tab: Corpus ───────────────────────────────────────────────────────────────
with tab_corpus:
    if not rag.has_index():
        st.info("Carga documentos desde el panel lateral para verlos aquí.")
    else:
        st.markdown(f"**{len(documents)} documento(s) indexado(s)**")
        for meta in documents.values():
            st.markdown(
                f"- **{meta['display_name']}** — "
                f"{meta['pages']} páginas · {meta['chunks']} chunks"
            )

# ── Tab: Chat ─────────────────────────────────────────────────────────────────
with tab_chat:

    # Historial
    if memory.is_empty():
        render_welcome()
    else:
        render_chat_history(memory)

    # Input
    user_input = st.chat_input("Escribe tu pregunta...")

    if user_input:
        # 1. Mostrar pregunta
        with st.chat_message("user"):
            st.markdown(user_input)
            from utils import now_str
            st.caption(now_str())

        # 2. RAG: recuperar contexto si hay índice
        context = ""
        if rag.has_index():
            chunks = rag.retrieve(user_input)
            context = rag.build_context(chunks)

        # 3. Construir system prompt
        system_prompt = build_system_prompt(st.session_state.mode, context)

        # 4. Registrar pregunta en memoria
        memory.add_user(user_input)

        # 5. Construir lista de mensajes LangChain
        lc_messages = memory.to_langchain(system_prompt)

        # 6. Invocar LLM
        llm = build_llm(st.session_state.llm_cfg)
        with st.chat_message("assistant"):
            with st.spinner(""):
                response_text = invoke(llm, lc_messages)
            st.markdown(response_text)
            st.caption(now_str())

        # 7. Guardar respuesta en memoria
        memory.add_assistant(response_text)
