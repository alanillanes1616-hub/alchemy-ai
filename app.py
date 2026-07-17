import streamlit as st
import google.generativeai as genai

# 1. Configuración de página
st.set_page_config(page_title="Asistente Lago Azul", layout="centered")

# 2. CSS para visibilidad (Forzamos fondo blanco y texto negro)
st.markdown("""
    <style>
    .stApp { background-color: white !important; }
    [data-testid="stChatMessage"] { background-color: #f0f2f6 !important; color: black !important; border-radius: 10px; }
    [data-testid="stChatMessage"] p { color: black !important; font-size: 15px; }
    #MainMenu, footer, header { visibility: hidden !important; }
    </style>
""", unsafe_allow_html=True)

# 3. Validación de API Key
api_key = st.secrets.get("GOOGLE_API_KEY")

if not api_key:
    st.error("Error: Configura 'GOOGLE_API_KEY' en los Secrets de Streamlit.")
    st.stop()

# 4. Inicialización del modelo (CAMBIO AQUÍ: 'gemini-pro' es universal)
try:
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-pro')
except Exception as e:
    st.error(f"Error al conectar con la API: {e}")
    st.stop()

# 5. Historial de mensajes
if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# 6. Lógica del Chat
if prompt := st.chat_input("¿En qué podemos asesorarte hoy?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Consultando..."):
            try:
                # El modelo 'gemini-pro' es el que tu librería actual aceptará sin error 404
                response = model.generate_content(f"Eres el asistente legal de Lago Azul, un despacho en El Alto, Bolivia. Responde profesionalmente: {prompt}")
                
                st.markdown(response.text)
                st.session_state.messages.append({"role": "assistant", "content": response.text})
            except Exception as e:
                st.error(f"Error al generar respuesta: {e}")
                