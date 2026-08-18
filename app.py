import os
import requests
import streamlit as st
import google.generativeai as genai

st.set_page_config(page_title="Clonador Viral IA", layout="wide")
st.title("🔗 Generador de Prompts desde un Enlace")
st.markdown("Pega un enlace de referencia (Shorts, TikTok, noticia o blog) para crear tu guion de 3 escenas y prompts.")

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
    st.sidebar.success(f"Pool Activo: {len(api_keys)}/15 Cuentas")
else:
    st.sidebar.error("⚠️ Agrega variables FLOW_KEY_1...15 en Render.")

url_input = st.text_input("🔗 Pega aquí el enlace de referencia:", placeholder="https://youtube.com/shorts/...")

estilo = st.selectbox(
    "🎨 Elige tu Estilo Visual para los Prompts:",
    [
        "3D Pixar / Personaje Animado (ej. Stickman 3D)", 
        "Macro ASMR / Texturas Hiperrealistas (ej. Tallado de frutas)", 
        "DIY / Escultura con Material Reciclado (ej. Personajes de anime)",
        "Cinematográfico / Realista"
    ]
)

def extraer_texto_de_url(url):
    try:
        respuesta = requests.get(f"https://r.jina.ai/{url}")
        if respuesta.status_code == 200:
            return respuesta.text
        else:
            return None
    except:
        return None

if st.button("🚀 Leer Enlace y Generar Prompts"):
    if not url_input:
        st.error("Por favor, pega un enlace válido.")
    else:
        current_key = obtener_siguiente_key()
        if not current_key:
            st.error("No hay claves API configuradas.")
        else:
            with st.spinner("🔍 Leyendo la información del enlace..."):
                texto_referencia = extraer_texto_de_url(url_input)
                
            if not texto_referencia:
                st.error("No se pudo extraer texto. Intenta con un enlace público diferente.")
            else:
                try:
                    genai.configure(api_key=current_key)
                    # CORRECCIÓN AQUÍ: Usamos el nombre del modelo más compatible
                    model_text = genai.GenerativeModel('gemini-1.5-flash')
                    
                    prompt_sistema = f"""
                    Eres un director experto en retención para videos verticales 9:16 (TikTok/Shorts/Reels).
                    Acabo de leer este contenido extraído de un enlace (puede ser el título, descripción o subtítulos de un video):
                    {texto_referencia[:3000]}...
                    
                    Tu tarea es adaptar la idea principal de ese texto a un guion de 3 escenas cortas.
                    El estilo visual para las imágenes debe ser: {estilo}.
                    
                    Usa ESTRICTAMENTE este formato:
                    
                    ESCENA 1 (0-4s):
                    - Subtítulo Español: [Gancho impactante basado en el link, con emojis]
                    - Prompt Imagen Inglés: [Prompt ultra detallado, formato 9:16 vertical, alta calidad, sin comillas]
                    - Prompt Video Inglés: [Prompt para animar la imagen con movimiento de cámara o personaje]

                    ESCENA 2 (4-8s):
                    - Subtítulo Español: [Desarrollo del tema del link]
                    - Prompt Imagen Inglés: [Prompt ultra detallado, formato 9:16 vertical]
                    - Prompt Video Inglés: [Prompt de animación fluida]

                    ESCENA 3 (8-12s):
                    - Subtítulo Español: [Cierre de la idea con llamado a la acción]
                    - Prompt Imagen Inglés: [Prompt ultra detallado, formato 9:16 vertical]
                    - Prompt Video Inglés: [Prompt de animación para un loop perfecto]
                    """
                    
                    with st.spinner("✍️ Creando guion y prompts basados en el enlace..."):
                        res_texto = model_text.generate_content(prompt_sistema)
                        
                        st.markdown("---")
                        st.subheader("📋 Resultados Listos")
                        st.write(res_texto.text)
                        
                        st.success("¡Listo! Copia los prompts en tu generador de imágenes y video favorito.")
                        
                except Exception as e:
                    # Respaldo por si la librería es muy antigua y pide el modelo anterior
                    if "404" in str(e) or "not found" in str(e):
                        try:
                            model_text_fallback = genai.GenerativeModel('gemini-1.0-pro')
                            res_texto = model_text_fallback.generate_content(prompt_sistema)
                            st.markdown("---")
                            st.subheader("📋 Resultados Listos (Versión Pro)")
                            st.write(res_texto.text)
                        except Exception as e2:
                            st.error(f"Error definitivo de modelo: {str(e2)}")
                    else:
                        st.error(f"Error al generar con la IA: {str(e)}")
                        
