import streamlit as st
import google.generativeai as genai

# 1. Configuración de página
st.set_page_config(page_title="Asistente Lago Azul", layout="centered")

# 2. CSS: fondo blanco, contraste legible y una identidad visual acorde
#    a un despacho legal (azul profundo + acentos dorados sutiles).
st.markdown("""
    <style>
    .stApp { background-color: #ffffff !important; }

    /* --- Caja de entrada de texto (chat_input) --- */
    /* Forzamos fondo claro en TODO el contenedor inferior, no solo el
       textarea, porque el tema oscuro de Streamlit pinta el wrapper. */
    [data-testid="stBottom"],
    [data-testid="stBottomBlockContainer"] {
        background-color: #ffffff !important;
    }

    [data-testid="stChatInput"] {
        background-color: #ffffff !important;
        border: 1px solid #cfe0ee !important;
        border-radius: 12px !important;
    }

    [data-testid="stChatInput"] textarea {
        background-color: #ffffff !important;
        color: #0f2942 !important;
        caret-color: #0f2942 !important;
    }

    [data-testid="stChatInput"] textarea::placeholder {
        color: #7a8a9a !important;
    }

    /* --- Burbujas de chat --- */
    [data-testid="stChatMessage"]:has(img[alt="user avatar"]) {
        background-color: #eaf1f8 !important;
        border: 1px solid #cfe0ee !important;
        border-radius: 12px;
    }

    [data-testid="stChatMessage"]:has(img[alt="assistant avatar"]) {
        background-color: #f9fafb !important;
        border: 1px solid #e3e6ea !important;
        border-left: 4px solid #b8935a !important;
        border-radius: 12px;
    }

    [data-testid="stChatMessage"] {
        background-color: #f7f9fb !important;
        border-radius: 12px;
        padding: 4px 2px;
    }

    [data-testid="stChatMessage"] p,
    [data-testid="stChatMessage"] li,
    [data-testid="stChatMessage"] span {
        color: #16263a !important;
        font-size: 15.5px !important;
        line-height: 1.55 !important;
    }

    [data-testid="stAlert"] p { color: #7a1f1f !important; }

    #MainMenu, footer, header { visibility: hidden !important; }
    </style>
""", unsafe_allow_html=True)

# 3. Validación de API Key
api_key = st.secrets.get("GOOGLE_API_KEY")

if not api_key:
    st.error("Error: Configura 'GOOGLE_API_KEY' en los Secrets de Streamlit.")
    st.stop()

# 4. Inicialización del modelo
try:
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-flash-latest')
except Exception as e:
    st.error(f"Error al conectar con la API: {e}")
    st.stop()

# 5. Historial de mensajes
if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])


# 6. Generador de texto en streaming
#    En vez de esperar la respuesta completa y mostrarla de golpe (lo que
#    hace que la página salte hasta el final), el texto va apareciendo
#    palabra por palabra, como una conversación real. Esto también evita
#    el salto brusco al fondo de la página.
def generar_respuesta_stream(prompt):
    respuesta = model.generate_content(
        f"Eres el asistente legal de Lago Azul, un despacho en El Alto, Bolivia. "
        f"Responde profesionalmente: {prompt}",
        stream=True,
    )
    for chunk in respuesta:
        if chunk.text:
            yield chunk.text


# 7. Lógica del Chat
if prompt := st.chat_input("¿En qué podemos asesorarte hoy?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        try:
            texto_completo = st.write_stream(generar_respuesta_stream(prompt))
            st.session_state.messages.append({"role": "assistant", "content": texto_completo})
        except Exception as e:
            st.error(f"Error al generar respuesta: {e}")
