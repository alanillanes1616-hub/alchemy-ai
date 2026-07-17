import streamlit as st
import google.generativeai as genai
import os

# 1. Configuración de página
st.set_page_config(page_title="Asistente Lago Azul", layout="centered")

# 2. CSS para visibilidad (Forzamos fondo blanco y texto negro)
st.markdown("""
    <style>
    .stApp { background-color: white !important; }
    [data-testid="stChatMessage"] { background-color: #f0f2f6 !important; color: black !important; }
    [data-testid="stChatMessage"] p { color: black !important; }
    #MainMenu, footer, header { visibility: hidden !important; }
    </style>
""", unsafe_allow_html=True)

# 3. Validación CRÍTICA de la API Key
api_key = st.secrets.get("GOOGLE_API_KEY")

if not api_key:
    st.error("Error: La variable 'GOOGLE_API_KEY' no se encuentra en los secretos de Streamlit. Por favor, configúrala en 'Secrets'.")
    st.stop()

# 4. Conexión a Gemini
try:
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-1.5-flash')
except Exception as e:
    st.error(f"Error fatal configurando Gemini: {e}")
    st.stop()

# 5. Historial
if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# 6. Chat funcional
if prompt := st.chat_input("¿En qué podemos asesorarte hoy?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Consultando al despacho legal..."):
            try:
                # Prompt directo sin dependencias externas complejas
                instruction = "Eres el asistente legal de Lago Azul, un despacho en El Alto, Bolivia. Responde de forma breve, profesional y clara."
                response = model.generate_content(f"{instruction} Consulta: {prompt}")
                
                st.markdown(response.text)
                st.session_state.messages.append({"role": "assistant", "content": response.text})
            except Exception as e:
                st.error(f"Error al obtener respuesta de Gemini: {e}")