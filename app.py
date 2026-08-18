import os
import streamlit as st
import google.generativeai as genai

st.set_page_config(page_title="Generador de Video IA", layout="wide")
st.title("🎬 Generador de Contenido Vertical (Prompts 9:16)")

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

idea_input = st.text_area("Escribe la idea, tema o concepto:", height=100)
estilo = st.selectbox(
    "Estilo Visual:",
    [
        "3D Pixar / Personaje Animado (Vertical 9:16)", 
        "Macro ASMR / Escultura Hiperrealista (Vertical 9:16)", 
        "DIY / Arte con Material Reciclado (Vertical 9:16)",
        "Cinematográfico (Vertical 9:16)"
    ]
)

if st.button("🚀 Generar Guion y Prompts"):
    if not idea_input:
        st.error("Ingresa una idea.")
    else:
        current_key = obtener_siguiente_key()
        if not current_key:
            st.error("No hay claves API configuradas.")
        else:
            try:
                genai.configure(api_key=current_key)
                
                model_text = genai.GenerativeModel('models/gemini-3.6-flash')
                
                prompt_sistema = f"""
                Actúa como director de contenido viral para TikTok, Shorts y Reels (formato vertical 9:16).
                Idea base: '{idea_input}'. Estilo visual: {estilo}.
                
                Crea un desglose exacto de 3 escenas cortas optimizadas para máxima retención y bucle (loop). 
                Usa estrictamente este formato para que sea fácil de leer:
                
                ESCENA 1 (0-4s):
                - Subtítulo: [Frase gancho atractiva con emojis]
                - Prompt: [Prompt detallado en inglés optimizado para generación de imagen/video vertical 9:16, iluminación y alta calidad]
                
                ESCENA 2 (4-8s):
                - Subtítulo: [Texto clave con emojis]
                - Prompt: [Prompt detallado en inglés para la segunda escena]
                
                ESCENA 3 (8-12s):
                - Subtítulo: [Llamado a la acción o cierre con emojis]
                - Prompt: [Prompt detallado en inglés optimizado para cierre en loop perfecto con la escena 1]
                """
                
                with st.spinner("Creando estructura viral..."):
                    res_texto = model_text.generate_content(prompt_sistema)
                    st.markdown("---")
                    st.subheader("📋 Tu Estructura y Prompts Listos")
                    st.write(res_texto.text)
                    st.success("¡Copia los prompts de arriba y pégalos en tu IA de video favorita para producirlos al instante!")
                    
            except Exception as e:
                st.error(f"Error al conectar con la API: {str(e)}")
            
