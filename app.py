import streamlit as st
from ui import inject_css, render_header, render_chat_history, render_welcome
from llm import build_llm, invoke, LLMConfig
from memory import ConversationMemory
from rag import RAGEngine
from config import DEFAULT_MODEL, DEFAULT_TEMPERATURE, DEFAULT_MAX_TOKENS

# Configuración inicial
st.set_page_config(page_title="Lago Azul AI", layout="wide", initial_sidebar_state="collapsed")
inject_css()

# Detectar si estamos en modo "camuflado" (incrustado)
is_embedded = st.query_params.get("embed") == "true"

# Estado
if "memory" not in st.session_state:
    st.session_state.memory = ConversationMemory()
if "rag" not in st.session_state:
    st.session_state.rag = RAGEngine(st.secrets["GOOGLE_API_KEY"])

# Lógica del Sidebar (Solo se muestra si NO está en modo embed)
if not is_embedded:
    with st.sidebar:
        st.markdown("### Administración")
        # Aquí puedes dejar tus herramientas de carga de documentos
        # ... (puedes copiar aquí tu lógica de `file_uploader` de tu app original)

# Área Principal
if not is_embedded:
    render_header("Asistente Legal")

# Lógica de Chat (Funciona igual, pero se ve limpia)
if st.session_state.memory.is_empty():
    if not is_embedded: render_welcome()
else:
    render_chat_history(st.session_state.memory)

user_input = st.chat_input("¿En qué podemos asesorarte hoy?")

if user_input:
    with st.chat_message("user"):
        st.markdown(user_input)
    
    # RAG funcional
    context = ""
    if st.session_state.rag.has_index():
        chunks = st.session_state.rag.retrieve(user_input)
        context = st.session_state.rag.build_context(chunks)

    # Invocación (Mantiene tu lógica de LLM original)
    llm = build_llm(LLMConfig(model=DEFAULT_MODEL, api_key=st.secrets["GOOGLE_API_KEY"]))
    response = invoke(llm, st.session_state.memory.to_langchain(f"Eres el asistente legal de Lago Azul. Contexto: {context}. Pregunta: {user_input}"))
    
    with st.chat_message("assistant"):
        st.markdown(response)
    
    st.session_state.memory.add_assistant(response)