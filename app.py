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

if st.button("🚀 Generar"):
    if not idea_input:
        st.error("Ingresa una idea.")
    else:
        current_key = obtener_siguiente_key()
        if not current_key:
            st.error("No hay claves API configuradas.")
        else:
            try:
                genai.configure(api_key=current_key)
                
                # ¡AQUÍ ESTÁ LA SOLUCIÓN! El modelo exacto que pide el error:
                model_text = genai.GenerativeModel('models/gemini-3.6-flash')
                
                prompt_sistema = f"""
                Actúa como director de contenido viral (9:16).
                Idea: '{idea_input}'. Estilo: {estilo}.
                
                Crea 3 escenas con esta estructura exacta:
                ESCENA 1:
                - Subtítulo: [Texto con emojis]
                - Prompt Imagen (Inglés): [Prompt 9:16 detallado en inglés]
                
                ESCENA 2:
                - Subtítulo: [Texto con emojis]
                - Prompt Imagen (Inglés): [Prompt 9:16 detallado en inglés]
                
                ESCENA 3:
                - Subtítulo: [Texto con emojis]
                - Prompt Imagen (Inglés): [Prompt 9:16 optimizado para loop]
                """
                
                with st.spinner("Procesando guion y prompts..."):
                    res_texto = model_text.generate_content(prompt_sistema)
                    st.markdown("---")
                    st.markdown(res_texto.text)
                    st.success("¡Prompts e instrucciones listos para usar!")
                    
            except Exception as e:
                st.error(f"Error al conectar con la API: {str(e)}")
                
