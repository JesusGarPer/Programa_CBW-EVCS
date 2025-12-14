import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import os
import sys
import glob

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Criptografía Visual - CBW-EVCS", layout="wide")

# --- IMPORTACIÓN DE LÓGICA ---
# Añadimos la carpeta Construcciones al path
sys.path.append(os.path.join(os.path.dirname(__file__), "Construcciones"))

try:
    from Construccion1 import CBWEVCS_Strict
    from Construccion2 import CBWEVCS_Construction2
    from Construccion3 import CBWEVCS_Construction3
    from Construccion4 import CBWEVCS_Construction4_Secure
    from Construccion5 import CBWEVCS_Construction5_PB
    from Construccion6_v2 import CBWEVCS_Universal_Kn_HighQuality
except ImportError as e:
    st.error(f"Error importando construcciones: {e}")

# --- FUNCIONES AUXILIARES (Reutilizadas) ---

def limpiar_archivos_previos(selection):
    folder = "ImagenesCreadas"
    if not os.path.exists(folder):
        return
    
    # Borrar cubiertas
    for f in glob.glob(os.path.join(folder, "cover*.png")):
        try: os.remove(f)
        except: pass

    # Borrar resultados específicos
    prefix = f"C{selection}_"
    files_to_remove = [f for f in os.listdir(folder) if f.startswith(prefix) and f.endswith(".png")]
    for filename in files_to_remove:
        try: os.remove(os.path.join(folder, filename))
        except: pass

def generate_source_images(n, secret_text, cover_text):
    output_dir = "ImagenesCreadas"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    def create_img(text, filename, is_secret=False):
        img = Image.new('1', (600, 400), color=1) 
        draw = ImageDraw.Draw(img)
        try:
            font = ImageFont.truetype("arial.ttf", 100 if is_secret else 80)
        except:
            font = ImageFont.load_default()
        
        # Centrado compatible
        try:
            left, top, right, bottom = draw.textbbox((0, 0), text, font=font)
            w, h = right - left, bottom - top
        except AttributeError:
            w, h = draw.textsize(text, font=font)
            
        x = (600 - w) / 2
        y = (400 - h) / 2
        draw.text((x, y), text, font=font, fill=0)
        path = os.path.join(output_dir, filename)
        img.save(path)
        return path

    path_secret = create_img(secret_text, "secret.png", is_secret=True)
    cover_paths = []
    for i in range(n):
        fname = f"cover{i+1}.png"
        create_img(f"{cover_text} {i+1}", fname)
        cover_paths.append(os.path.join(output_dir, fname))
    return path_secret, cover_paths

# --- INTERFAZ GRÁFICA WEB ---

st.title("🔐 Generador CBW-EVCS Web")
st.markdown("Interfaz para Criptografía Visual Extendida basada en Color")

# Barra lateral para configuración
with st.sidebar:
    st.header("1. Configuración")
    
    secret_txt = st.text_input("Texto Secreto", value="HOLA")
    cover_txt = st.text_input("Texto Cubiertas", value="USER")
    
    st.divider()
    
    st.header("2. Algoritmo")
    construction_type = st.selectbox(
        "Elige la Construcción",
        options=["1", "2", "3", "4", "5", "6"],
        format_func=lambda x: f"Construcción {x}"
    )
    
    # Lógica dinámica de inputs
    if construction_type in ["1", "2", "3"]:
        k_val = 2
        n_val = 2
        st.info("🔒 Para C1, C2 y C3, k=2 y n=2 fijos.")
    elif construction_type in ["4", "5"]:
        k_val = 2
        n_val = st.number_input("Participantes (n)", min_value=2, value=3)
        st.info("🔒 Para C4 y C5, k=2 fijo.")
    else: # Construcción 6
        k_val = st.number_input("Umbral (k)", min_value=2, value=3)
        default_n = max(4, k_val)
        n_val = st.number_input("Participantes (n)", min_value=k_val, value=default_n)

    st.divider()
    
    btn_run = st.button("🚀 GENERAR Y PROCESAR", type="primary")

# --- LÓGICA DE EJECUCIÓN ---

if btn_run:
    output_dir = "ImagenesCreadas"
    
    with st.spinner('Limpiando y Procesando...'):
        # 1. Limpieza
        limpiar_archivos_previos(construction_type)
        
        # 2. Generación Base
        secret_path, cover_paths = generate_source_images(n_val, secret_txt, cover_txt)
        
        processor = None
        
        # 3. Ejecución de Construcciones (Tu lógica exacta)
        try:
            if construction_type == "1":
                processor = CBWEVCS_Strict()
                s1, s2 = processor.process_images(secret_path, cover_paths[0], cover_paths[1])
                s1.save(os.path.join(output_dir, "C1_shadow1.png"))
                s2.save(os.path.join(output_dir, "C1_shadow2.png"))
                processor.simulate_stacking(s1, s2).save(os.path.join(output_dir, "C1_stacked.png"))

            elif construction_type == "2":
                processor = CBWEVCS_Construction2()
                s1, s2 = processor.process_images(secret_path, cover_paths[0], cover_paths[1])
                s1.save(os.path.join(output_dir, "C2_shadow1.png"))
                s2.save(os.path.join(output_dir, "C2_shadow2.png"))
                processor.simulate_stacking(s1, s2).save(os.path.join(output_dir, "C2_stacked.png"))

            elif construction_type == "3":
                processor = CBWEVCS_Construction3()
                s1, s2 = processor.process_images(secret_path, cover_paths[0], cover_paths[1])
                s1.save(os.path.join(output_dir, "C3_shadow1.png"))
                s2.save(os.path.join(output_dir, "C3_shadow2.png"))
                processor.simulate_stacking(s1, s2).save(os.path.join(output_dir, "C3_stacked.png"))

            elif construction_type == "4":
                processor = CBWEVCS_Construction4_Secure(n_participants=n_val)
                shadows = processor.process_images(secret_path, cover_paths)
                for i, s in enumerate(shadows):
                    s.save(os.path.join(output_dir, f"C4_shadow{i+1}.png"))
                
                # Pares
                for i in range(len(shadows)):
                    for j in range(i + 1, len(shadows)):
                        res = processor.simulate_stacking(shadows[i], shadows[j])
                        res.save(os.path.join(output_dir, f"C4_stacked_{i+1}y{j+1}.png"))
                
                # Total
                stacked_all = shadows[0]
                for i in range(1, len(shadows)):
                    stacked_all = processor.simulate_stacking(stacked_all, shadows[i])
                stacked_all.save(os.path.join(output_dir, "C4_stacked_ALL.png"))

            elif construction_type == "5":
                processor = CBWEVCS_Construction5_PB(n_participants=n_val)
                shadows = processor.process_images(secret_path, cover_paths)
                for i, s in enumerate(shadows):
                    s.save(os.path.join(output_dir, f"C5_shadow{i+1}.png"))
                
                # Pares
                for i in range(len(shadows)):
                    for j in range(i + 1, len(shadows)):
                        res = processor.simulate_stacking(shadows[i], shadows[j])
                        res.save(os.path.join(output_dir, f"C5_stacked_{i+1}y{j+1}.png"))
                
                # Total
                stacked_all = shadows[0]
                for i in range(1, len(shadows)):
                    stacked_all = processor.simulate_stacking(stacked_all, shadows[i])
                stacked_all.save(os.path.join(output_dir, "C5_stacked_ALL.png"))

            elif construction_type == "6":
                processor = CBWEVCS_Universal_Kn_HighQuality(k=k_val, n=n_val, d=3)
                shadows = processor.process_images(secret_path, cover_paths)
                
                if shadows:
                    for i, s in enumerate(shadows):
                        s.save(os.path.join(output_dir, f"C6_Shadow_Final_User{i+1}.png"))
                    
                    if k_val > 1:
                        res_fail = processor.simulate_stacking(shadows[:k_val-1])
                        res_fail.save(os.path.join(output_dir, f"C6_Test_Security_{k_val-1}_of_{n_val}.png"))
                    
                    res_success = processor.simulate_stacking(shadows[:k_val])
                    res_success.save(os.path.join(output_dir, f"C6_Test_Success_{k_val}_of_{n_val}.png"))
                    
                    if n_val > k_val:
                        res_all = processor.simulate_stacking(shadows)
                        res_all.save(os.path.join(output_dir, f"C6_Test_ALL_{n_val}_of_{n_val}.png"))

            st.success("¡Proceso completado!")
            
        except Exception as e:
            st.error(f"Error: {e}")

# --- MOSTRAR RESULTADOS (GALERÍA) ---
output_dir = "ImagenesCreadas"
if os.path.exists(output_dir):
    # Obtener archivos generados actualmente
    prefix = f"C{construction_type}_" if 'construction_type' in locals() else ""
    
    # Filtrar solo imágenes relevantes a la selección actual o mostrar nada si no se ha corrido
    images = sorted([f for f in os.listdir(output_dir) if f.startswith(prefix) and f.endswith(".png")])
    
    if images:
        st.divider()
        st.subheader("📸 Resultados")
        
        # Separar en Sombras y Stacked para mejor visualización
        shadows_files = [img for img in images if "shadow" in img.lower() or "shadow" in img]
        stacked_files = [img for img in images if "stacked" in img.lower() or "test" in img.lower()]
        
        if shadows_files:
            st.write("**Sombras Generadas (Lo que recibe cada usuario):**")
            cols = st.columns(len(shadows_files))
            for i, img_file in enumerate(shadows_files):
                # Mostrar en rejilla, haciendo wrap si hay muchas
                with cols[i % len(cols)]:
                    st.image(os.path.join(output_dir, img_file), caption=img_file, use_container_width=True)

        if stacked_files:
            st.write("**Pruebas de Apilamiento (Resultados al juntar):**")
            # Rejilla adaptativa
            cols_stack = st.columns(min(len(stacked_files), 3))
            for i, img_file in enumerate(stacked_files):
                 with cols_stack[i % 3]:
                    st.image(os.path.join(output_dir, img_file), caption=img_file, use_container_width=True)