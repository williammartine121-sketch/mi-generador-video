import os
import streamlit as st
import google.generativeai as genai
from PIL import Image
import io

st.set_page_config(page_title="Generador de Video e Imágenes IA", layout="wide")
st.title("🎬 Generador de Contenido Vertical (Prompts e Imágenes 9:16)")

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
    ["3D Pixar / Animación (Vertical 9:16)", "Macro ASMR / Realista (Vertical 9:16)", "Cinematográfico (Vertical 9:16)"]
)

if st.button("🚀 Generar"):
    if not idea_input:
        st.error("Ingresa una idea.")
    else:
        current_key = obtener_siguiente_key()
        if not current_key:
            st.error("No hay claves API.")
        else:
            try:
                genai.configure(api_key=current_key)
                model_text = genai.GenerativeModel('gemini-1.5-flash')
                prompt_sistema = f"Crea 3 escenas (9:16) para: '{idea_input}'. Estilo: {estilo}. Dame: Subtítulo y Prompt de Imagen en Inglés detallado para cada escena."
                
                with st.spinner("Procesando..."):
                    res_texto = model_text.generate_content(prompt_sistema)
                    st.write(res_texto.text)
                    
                    st.subheader("🖼️ Imágenes")
                    # Intento de extracción simple
                    lines = res_texto.text.split("\n")
                    prompts = [l.replace("- Prompt Imagen (Inglés):", "").strip() for l in lines if "Prompt Imagen" in l]
                    
                    if not prompts: prompts = [f"Vertical 9:16 shot of {idea_input}, highly detailed"]
                    
                    imagen_model = genai.GenerativeModel('imagen-3.0-generate-002')
                    for p in prompts[:3]:
                        result = imagen_model.generate_images(prompt=p, number_of_images=1, aspect_ratio="9:16")
                        for gen_img in result.generated_images:
                            image = Image.open(io.BytesIO(gen_img.image.image_bytes))
                            st.image(image, use_column_width=True)
            except Exception as e:
                st.error(f"Error: {str(e)}")
            
