import streamlit as st
import google.generativeai as genai

# 1. Configuración de página
st.set_page_config(page_title="Asistente Lago Azul", layout="centered")

# 2. CSS para "Camuflaje" (Fondo blanco, texto negro, sin elementos de Streamlit)
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

# 4. Inicialización del modelo (Usando la versión más estable y actual: gemini-1.5-pro)
try:
    genai.configure(api_key=api_key)
    # gemini-1.5-pro es el estándar actual y más compatible
    model = genai.GenerativeModel('gemini-1.5-pro')
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
                # Instrucción de sistema
                instruction = "Eres el asistente legal de Lago Azul, un despacho en El Alto, Bolivia. Responde de forma profesional, breve y clara."
                
                # Generación de respuesta
                response = model.generate_content(f"{instruction} Consulta: {prompt}")
                
                # Renderizado
                st.markdown(response.text)
                st.session_state.messages.append({"role": "assistant", "content": response.text})
            except Exception as e:
                st.error(f"Error al generar respuesta: {e}")