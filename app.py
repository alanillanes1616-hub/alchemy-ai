import streamlit as st
from llm import build_llm, invoke, LLMConfig
from memory import ConversationMemory

# 1. Configuración de página
st.set_page_config(page_title="Asistente Lago Azul", layout="centered")

# 2. CSS Mejorado para legibilidad total
st.markdown("""
    <style>
    /* Fondo principal blanco y texto negro */
    .stApp { background-color: white !important; color: black !important; }
    
    /* Asegurar que el texto del chat sea negro */
    [data-testid="stChatMessage"] { color: black !important; }
    div[data-testid="stChatMessage"] p { color: black !important; }
    
    /* Ocultar elementos de Streamlit que ensucian la vista */
    #MainMenu, footer, header { visibility: hidden !important; }
    
    /* Input de texto con borde visible y texto negro */
    [data-testid="stChatInput"] textarea { color: black !important; }
    </style>
""", unsafe_allow_html=True)

# 3. Inicializar memoria y motor
if "memory" not in st.session_state:
    st.session_state.memory = ConversationMemory()

# 4. Mostrar historial existente
for msg in st.session_state.memory.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# 5. Lógica de respuesta real
if prompt := st.chat_input("¿En qué podemos asesorarte hoy?"):
    # Mostrar mensaje usuario
    st.session_state.memory.add_user(prompt)
    with st.chat_message("user"):
        st.markdown(prompt)

    # Procesar respuesta con tu IA
    with st.chat_message("assistant"):
        with st.spinner("Pensando..."):
            try:
                # Configuración del LLM usando tu arquitectura
                llm = build_llm(LLMConfig(
                    model="gemini-1.5-flash", 
                    api_key=st.secrets["GOOGLE_API_KEY"]
                ))
                
                # Invocación real a tu motor
                system_prompt = "Eres el asistente legal de Lago Azul. Responde de forma profesional."
                response = invoke(llm, st.session_state.memory.to_langchain(system_prompt))
                
                st.markdown(response)
                st.session_state.memory.add_assistant(response)
            except Exception as e:
                st.error("Hubo un error al procesar tu consulta.")