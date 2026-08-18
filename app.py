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
    [
        "3D Pixar / Personaje Animado (Vertical 9:16)", 
        "Macro ASMR / Escultura Hiperrealista (Vertical 9:16)", 
        "DIY / Arte con Material Reciclado (Vertical 9:16)",
        "Cinematográfico (Vertical 9:16)"
    ]
)

if st.button("🚀 Generar Guion e Imágenes"):
    if not idea_input:
        st.error("Ingresa una idea.")
    else:
        current_key = obtener_siguiente_key()
        if not current_key:
            st.error("No hay claves API configuradas.")
        else:
            try:
                genai.configure(api_key=current_key)
                
                # 1. Generar texto y prompts
                model_text = genai.GenerativeModel('models/gemini-3.6-flash')
                prompt_sistema = f"""
                Actúa como director de contenido viral (9:16). Idea: '{idea_input}'. Estilo: {estilo}.
                Crea 3 escenas. Usa estrictamente este formato:
                ESCENA 1:
                - Subtítulo: [Texto con emojis]
                - Prompt: [Prompt detallado en inglés para imagen vertical 9:16]
                ESCENA 2:
                - Subtítulo: [Texto con emojis]
                - Prompt: [Prompt detallado en inglés para imagen vertical 9:16]
                ESCENA 3:
                - Subtítulo: [Texto con emojis]
                - Prompt: [Prompt detallado en inglés para imagen vertical 9:16 en loop]
                """
                
                with st.spinner("Creando guion y estructurando escenas..."):
                    res_texto = model_text.generate_content(prompt_sistema)
                    st.markdown("---")
                    st.subheader("📋 Guion y Subtítulos")
                    st.write(res_texto.text)
                
                # 2. Generar imágenes una por una
                st.markdown("---")
                st.subheader("🖼️ Generando Imágenes en Pantalla (Espera un momento...)")
                
                lines = res_texto.text.split("\n")
                prompts_imagen = []
                for l in lines:
                    if "- Prompt:" in l or "Prompt:" in l:
                        clean_p = l.split(":", 1)[-1].strip()
                        if clean_p:
                            prompts_imagen.append(clean_p)
                
                if not prompts_imagen:
                    prompts_imagen = [f"Vertical 9:16 shot of {idea_input}, {estilo}, highly detailed"] * 3
                
                for idx, p_img in enumerate(prompts_imagen[:3]):
                    st.markdown(f"**Generando Imagen de la Escena {idx+1}...**")
                    try:
                        with st.spinner(f"Renderizando imagen {idx+1}, por favor espera..."):
                            # Usar modelo de imágenes compatible
                            imagen_model = genai.GenerativeModel('imagen-3.0-generate-002')
                            result = imagen_model.generate_images(
                                prompt=p_img,
                                number_of_images=1,
                                aspect_ratio="9:16"
                            )
                            for generated_image in result.generated_images:
                                image = Image.open(io.BytesIO(generated_image.image.image_bytes))
                                st.image(image, use_column_width=True)
                    except Exception as img_err:
                        st.info(f"Nota en Escena {idx+1}: Usando respaldo de prompt debido a restricción de cuota de imagen en esta cuenta.")
                        st.code(p_img)

                st.success("¡Proceso finalizado!")

            except Exception as e:
                st.error(f"Error: {str(e)}")
                            
