import streamlit as st
import os

# 1. Configuración de página minimalista
st.set_page_config(page_title="Asistente Lago Azul", layout="centered")

# 2. Estilos para "camuflar" (Forzar fondo blanco y ocultar elementos de Streamlit)
st.markdown("""
    <style>
    /* Forzar fondo blanco y eliminar bordes de Streamlit */
    .stApp { background-color: white !important; }
    #MainMenu, footer, header { visibility: hidden !important; }
    
    /* Hacer que el contenedor sea limpio */
    section[data-testid="stSidebar"] { display: none !important; }
    </style>
""", unsafe_allow_html=True)

# 3. Inicialización básica de mensajes
if "messages" not in st.session_state:
    st.session_state.messages = []

# 4. Mostrar historial
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# 5. Lógica del chat (Sin llamadas externas complejas por ahora)
if prompt := st.chat_input("¿En qué podemos asesorarte hoy?"):
    # Guardar y mostrar usuario
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Respuesta del asistente
    with st.chat_message("assistant"):
        # Mensaje temporal mientras verificas la integración
        respuesta = "Hola, soy el asistente de Lago Azul. Estamos optimizando tu consulta. ¡En breve te atenderemos!"
        st.markdown(respuesta)
    
    st.session_state.messages.append({"role": "assistant", "content": respuesta})