import streamlit as st
import google.generativeai as genai

# 1. Configuración de página
st.set_page_config(page_title="Asistente Lago Azul", layout="centered")

# 2. CSS para "Camuflaje" y Legibilidad
# El fondo es transparente para que herede el color de tu web.
st.markdown("""
    <style>
    /* Hacer transparente todo el contenedor de Streamlit */
    .stApp { background: transparent !important; }
    
    /* Forzar que el texto sea negro y el chat se vea decente */
    [data-testid="stChatMessage"] { background-color: rgba(255, 255, 255, 0.9) !important; color: black !important; }
    [data-testid="stChatMessage"] p { color: black !important; font-size: 16px; }
    
    /* Ocultar elementos de Streamlit para que parezca parte de tu web */
    #MainMenu, footer, header { visibility: hidden !important; }
    
    /* Estilo del input */
    [data-testid="stChatInput"] { background-color: transparent !important; }
    </style>
""", unsafe_allow_html=True)

# 3. Inicializar Gemini
# Asegúrate de tener GOOGLE_API_KEY en tus "Secrets" de Streamlit Cloud
genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
model = genai.GenerativeModel('gemini-1.5-flash')

# 4. Estado de la conversación
if "messages" not in st.session_state:
    st.session_state.messages = []

# 5. Mostrar historial
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# 6. Lógica de consulta (Motor de búsqueda/IA)
if prompt := st.chat_input("¿En qué podemos asesorarte hoy?"):
    # Mostrar mensaje del usuario
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Respuesta de la IA
    with st.chat_message("assistant"):
        try:
            # System prompt para que actúe como abogado de Lago Azul
            instruction = "Eres el asistente legal de Lago Azul. Responde de forma profesional, breve y clara."
            full_query = f"{instruction} Pregunta: {prompt}"
            
            response = model.generate_content(full_query)
            
            st.markdown(response.text)
            st.session_state.messages.append({"role": "assistant", "content": response.text})
            
        except Exception as e:
            st.error("Lo sentimos, estamos teniendo problemas técnicos. Inténtalo de nuevo.")