import streamlit as st
from llm import build_llm, invoke, LLMConfig
from memory import ConversationMemory
from prompts import build_system_prompt

# ── Configuración Minimalista ─────────────────────────────────────────────────
st.set_page_config(page_title="Asistente Lago Azul", layout="centered")

# Ocultar elementos de Streamlit para que sea "camuflado"
hide_streamlit_style = """
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    </style>
"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

# ── Estado de sesión ─────────────────────────────────────────────────────────
if "memory" not in st.session_state:
    st.session_state.memory = ConversationMemory()

# ── Lógica del Chat ──────────────────────────────────────────────────────────
# Prompt fijo para tu despacho legal
SYSTEM_PROMPT = """Eres el asistente virtual del despacho legal "Lago Azul". 
Tu objetivo es responder consultas legales de forma clara, profesional y empática. 
Si la consulta es compleja, sugiere al usuario contactar por WhatsApp."""

# Renderizado del chat
for msg in st.session_state.memory.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if user_input := st.chat_input("¿En qué podemos asesorarte hoy?"):
    with st.chat_message("user"):
        st.markdown(user_input)
    
    st.session_state.memory.add_user(user_input)
    
    # Invocación (Asegúrate de tener tus módulos de llm.py funcionando)
    llm = build_llm(LLMConfig(model="gemini-1.5-flash", api_key=st.secrets["GOOGLE_API_KEY"]))
    response = invoke(llm, st.session_state.memory.to_langchain(SYSTEM_PROMPT))
    
    with st.chat_message("assistant"):
        st.markdown(response)
    
    st.session_state.memory.add_assistant(response)