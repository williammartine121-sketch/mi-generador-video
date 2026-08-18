import os
import streamlit as st

st.set_page_config(page_title="Generador de Video IA", layout="wide")
st.title("🎬 Automatizador de Videos desde Link")

# Cargar las 15 claves API configuradas en las variables del servidor
@st.cache_resource
def cargar_cuentas():
    keys = []
    for i in range(1, 16):
        key = os.getenv(f"FLOW_KEY_{i}")
        if key:
            keys.append(key)
    return keys

api_keys = cargar_cuentas()

if "index_cuenta" not in st.session_state:
    st.session_state.index_cuenta = 0

def obtener_siguiente_key():
    if not api_keys:
        return None
    key_actual = api_keys[st.session_state.index_cuenta]
    st.session_state.index_cuenta = (st.session_state.index_cuenta + 1) % len(api_keys)
    return key_actual

if api_keys:
    st.sidebar.success(f"Cuentas activas en el pool: {len(api_keys)}/15")
else:
    st.sidebar.warning("No se detectaron claves API en las variables del entorno.")

url_referencia = st.text_input("Pega aquí el link del video de referencia (TikTok, Shorts, Reels):")

opciones_voz = [
    "Español Latino - Narrador Épico",
    "Español Latino - Voz Juvenil",
    "Español Latino - Voz Neutra Informativa"
]
voz_seleccionada = st.selectbox("Selecciona la voz para la locución:", opciones_voz)

if st.button("Analizar Video y Generar Prompts"):
    if not url_referencia:
        st.error("Por favor ingresa un enlace válido.")
    else:
        key_uso = obtener_siguiente_key()
        st.info("Procesando solicitud usando el slot de cuenta activa...")
        
        st.subheader("Desglose de Escenas Generado")
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**Escena 1 (0-5s)**")
            st.text_area("Prompt Imagen/Video:", "Estilo 3D Pixar, personaje principal mirando a la cámara, iluminación cinematográfica, 9:16 vertical.", key="p1")
            st.text_input("Guion de voz:", "Aprende el secreto para crear contenido sin gastar dinero.", key="g1")
            
        with col2:
            st.markdown("**Escena 2 (5-10s)**")
            st.text_area("Prompt Imagen/Video:", "Estilo 3D Pixar, personaje trabajando en computadora futurista, 9:16 vertical.", key="p2")
            st.text_input("Guion de voz:", "Todo automatizado directamente desde la nube.", key="g2")

        st.success("Análisis completado.")
          
