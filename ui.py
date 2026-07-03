"""
ui.py — Estilos CSS y componentes reutilizables de la interfaz.
"""

import streamlit as st

from config import MODES
from memory import ConversationMemory


# ── CSS ───────────────────────────────────────────────────────────────────────

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', 'Segoe UI', sans-serif !important;
    background-color: #f9fafb !important;
    color: #111827 !important;
}

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background-color: #f3f4f6 !important;
    border-right: 1px solid #e5e7eb !important;
    padding-top: 1rem;
}
[data-testid="stSidebar"] * { color: #111827 !important; }
[data-testid="stSidebar"] .stSelectbox label,
[data-testid="stSidebar"] .stSlider label { font-size: 12px; color: #6b7280 !important; }

/* ── Chat messages ── */
[data-testid="stChatMessage"] {
    background-color: #ffffff !important;
    border: 1px solid #e5e7eb !important;
    border-radius: 8px !important;
    padding: 12px 16px !important;
    margin-bottom: 8px !important;
    box-shadow: 0 1px 2px rgba(0,0,0,0.04);
}

/* ── Chat input ── */
[data-testid="stChatInput"] textarea {
    background-color: #ffffff !important;
    border: 1px solid #d1d5db !important;
    border-radius: 8px !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 14px !important;
}
[data-testid="stChatInput"] textarea:focus {
    border-color: #1d4ed8 !important;
    box-shadow: 0 0 0 2px rgba(29,78,216,0.12) !important;
}

/* ── Botones primarios ── */
.stButton > button {
    background-color: #1d4ed8 !important;
    color: #ffffff !important;
    border: none !important;
    border-radius: 6px !important;
    font-size: 13px !important;
    font-weight: 500 !important;
    padding: 6px 16px !important;
    transition: background-color 0.15s ease;
}
.stButton > button:hover { background-color: #1e40af !important; }

/* ── Botón secundario (limpiar, etc.) ── */
.secondary-btn > button {
    background-color: #f3f4f6 !important;
    color: #374151 !important;
    border: 1px solid #d1d5db !important;
}
.secondary-btn > button:hover { background-color: #e5e7eb !important; }

/* ── Tabs ── */
.stTabs [data-baseweb="tab"] {
    font-size: 13px;
    font-weight: 500;
    color: #6b7280;
}
.stTabs [aria-selected="true"] {
    color: #1d4ed8 !important;
    border-bottom: 2px solid #1d4ed8 !important;
}

/* ── Selectbox / sliders ── */
[data-baseweb="select"] { border-radius: 6px !important; }

/* ── File uploader ── */
[data-testid="stFileUploader"] {
    border: 1px dashed #d1d5db !important;
    border-radius: 8px !important;
    background-color: #f9fafb !important;
}

/* ── Badges de modo ── */
.mode-badge {
    display: inline-block;
    background-color: #eff6ff;
    color: #1d4ed8;
    font-size: 11px;
    font-weight: 600;
    padding: 2px 10px;
    border-radius: 999px;
    border: 1px solid #bfdbfe;
    margin-bottom: 4px;
}

/* ── Divisores ── */
hr { border-color: #e5e7eb !important; margin: 8px 0 !important; }

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 5px; }
::-webkit-scrollbar-track { background: #f3f4f6; }
::-webkit-scrollbar-thumb { background: #d1d5db; border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: #9ca3af; }

/* ── Code blocks ── */
code, pre {
    background-color: #f3f4f6 !important;
    border: 1px solid #e5e7eb !important;
    border-radius: 4px !important;
    font-size: 12px !important;
}
</style>
"""


def inject_css() -> None:
    """Inyecta el CSS global de la aplicación."""
    st.markdown(CSS, unsafe_allow_html=True)


# ── Header ────────────────────────────────────────────────────────────────────

def render_header(mode: str) -> None:
    """Renderiza el encabezado principal con el modo activo."""
    st.markdown(
        f"""
        <div style="margin-bottom: 4px;">
            <span style="font-size:22px; font-weight:600; color:#111827;">Alchemy AI</span>
            &nbsp;
            <span class="mode-badge">{mode}</span>
        </div>
        <p style="font-size:13px; color:#6b7280; margin-top:0;">
            Asistente de investigación científica · RAG + Gemini
        </p>
        """,
        unsafe_allow_html=True,
    )
    st.markdown("---")


# ── Chat ──────────────────────────────────────────────────────────────────────

def render_chat_history(memory: ConversationMemory) -> None:
    """Renderiza el historial de mensajes en el área de chat."""
    for msg in memory.messages:
        role = "user" if msg.role == "user" else "assistant"
        with st.chat_message(role):
            st.markdown(msg.content)
            st.caption(msg.timestamp)


# ── Document list ─────────────────────────────────────────────────────────────

def render_document_list(documents: dict[str, dict]) -> list[str]:
    """
    Muestra la lista de documentos con opción de eliminar.

    Args:
        documents: dict {filename: {"pages": int, "chunks": int}}.

    Returns:
        Lista de nombres de documentos marcados para eliminar.
    """
    to_remove = []
    if not documents:
        st.caption("Sin documentos cargados.")
        return to_remove

    for name, meta in documents.items():
        col1, col2 = st.columns([4, 1])
        with col1:
            st.markdown(
                f"<span style='font-size:12px;'>{name}</span><br>"
                f"<span style='font-size:10px; color:#9ca3af;'>"
                f"{meta.get('pages', 0)} págs · {meta.get('chunks', 0)} chunks</span>",
                unsafe_allow_html=True,
            )
        with col2:
            if st.button("x", key=f"del_{name}", help=f"Eliminar {name}"):
                to_remove.append(name)
    return to_remove


# ── Empty state ───────────────────────────────────────────────────────────────

def render_welcome() -> None:
    """Mensaje de bienvenida cuando el chat está vacío."""
    st.markdown(
        """
        <div style="text-align:center; padding: 60px 20px; color:#9ca3af;">
            <div style="font-size:36px; margin-bottom:12px;">&#9670;</div>
            <p style="font-size:15px; font-weight:500; color:#6b7280;">
                Bienvenido a Alchemy AI
            </p>
            <p style="font-size:13px;">
                Haz una pregunta o carga documentos desde el panel lateral para comenzar.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

