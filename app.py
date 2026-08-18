import os
import urllib.parse
import streamlit as st
import google.generativeai as genai

st.set_page_config(page_title="Generador Total IA", layout="wide")
st.title("🎬 Creador de Contenido Vertical (Imágenes y Prompts)")

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

idea_input = st.text_area("Escribe la idea para tu video:", height=80)
estilo = st.selectbox(
    "Estilo Visual:",
    [
        "3D Pixar / Personaje Animado", 
        "Macro ASMR / Hiperrealista", 
        "DIY / Reciclaje",
        "Cinematográfico Oscuro"
    ]
)

if st.button("🚀 Generar Imágenes y Guion Total"):
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
                Eres un director de videos virales (9:16). Idea: '{idea_input}'. Estilo: {estilo}.
                Crea 3 escenas. Debes seguir ESTRICTAMENTE este formato para que el sistema funcione:

                ESCENA 1:
                VOZ EN OFF ESPAÑOL: [Lo que la IA de voz dirá]
                PROMPT_IMAGEN_INGLES: [Prompt detallado en inglés para generar la imagen estática vertical, sin comillas]
                PROMPT_VIDEO_INGLES: [Prompt en inglés para animar la imagen en Luma o Gen-3]

                ESCENA 2:
                VOZ EN OFF ESPAÑOL: [Lo que la IA de voz dirá]
                PROMPT_IMAGEN_INGLES: [Prompt detallado en inglés]
                PROMPT_VIDEO_INGLES: [Prompt en inglés para animar la imagen]

                ESCENA 3:
                VOZ EN OFF ESPAÑOL: [Llamado a la acción]
                PROMPT_IMAGEN_INGLES: [Prompt detallado en inglés]
                PROMPT_VIDEO_INGLES: [Prompt en inglés para animar en loop]
                """
                
                with st.spinner("🧠 Pensando guion y dibujando imágenes..."):
                    res_texto = model_text.generate_content(prompt_sistema)
                    texto_generado = res_texto.text
                    
                    st.markdown("---")
                    st.subheader("📋 Tu Guion de Trabajo")
                    st.write(texto_generado)
                    
                    st.markdown("---")
                    st.subheader("🖼️ Tus Imágenes Base Generadas (Listas para animar)")
                    
                    # Extraer los prompts de imagen para renderizarlos
                    lineas = texto_generado.split('\n')
                    prompts_imagenes = []
                    for linea in lineas:
                        if "PROMPT_IMAGEN_INGLES:" in linea:
                            # Limpiar el texto
                            prompt_limpio = linea.replace("PROMPT_IMAGEN_INGLES:", "").strip()
                            # Añadir palabras clave para asegurar formato vertical y calidad
                            prompt_completo = f"{prompt_limpio}, vertical 9:16 format, highly detailed, masterpiece"
                            prompts_imagenes.append(prompt_completo)
                    
                    if prompts_imagenes:
                        cols = st.columns(len(prompts_imagenes[:3]))
                        for idx, p_img in enumerate(prompts_imagenes[:3]):
                            with cols[idx]:
                                st.caption(f"**Escena {idx+1}**")
                                # Usar Pollinations AI (API gratuita sin key)
                                url_imagen = f"https://image.pollinations.ai/prompt/{urllib.parse.quote(p_img)}?width=576&height=1024&nologo=true"
                                st.image(url_imagen, use_column_width=True)
                    else:
                        st.warning("No se pudieron extraer los prompts de imagen. Intenta generar de nuevo.")
                        
                st.success("✅ ¡Listo! Guarda estas imágenes. Luego llévalas a tu IA de video junto con el 'PROMPT_VIDEO_INGLES'. Al final, ponle la 'VOZ EN OFF ESPAÑOL' en CapCut.")

            except Exception as e:
                st.error(f"Error: {str(e)}")
