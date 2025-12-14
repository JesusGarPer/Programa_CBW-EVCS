import random
from PIL import Image
import os

class CBWEVCS_Strict:
    def __init__(self):
        self.RED = (255, 0, 0)
        self.GREEN = (0, 255, 0)
        self.BLUE = (0, 0, 255)
        self.BLACK = (0, 0, 0)
        self.COLORS = [self.RED, self.GREEN, self.BLUE]

    def _get_random_color(self):
        return random.choice(self.COLORS)

    def _get_different_color(self, color_to_avoid):
        candidates = [c for c in self.COLORS if c != color_to_avoid]
        return random.choice(candidates)

    def process_images(self, secret_path, cover1_path, cover2_path):
        # Cargar y convertir a binario estricto (1-bit)
        secret_img = Image.open(secret_path).convert('1')
        cover1_img = Image.open(cover1_path).convert('1')
        cover2_img = Image.open(cover2_path).convert('1')

        width, height = secret_img.size
        cover1_img = cover1_img.resize((width, height))
        cover2_img = cover2_img.resize((width, height))

        # Imagen de salida: Ancho x 2 (Expansión m=2)
        out_shadow1 = Image.new('RGB', (width * 2, height))
        out_shadow2 = Image.new('RGB', (width * 2, height))
        
        s_pixels = secret_img.load()
        c1_pixels = cover1_img.load()
        c2_pixels = cover2_img.load()
        out1_pixels = out_shadow1.load()
        out2_pixels = out_shadow2.load()

        print("Procesando con lógica estricta de Columnas...")

        for y in range(height):
            for x in range(width):
                # 0 = Negro (Tinta/Info), 1 = Blanco (Transparente)
                s = 0 if s_pixels[x, y] == 0 else 1
                c1 = 0 if c1_pixels[x, y] == 0 else 1
                c2 = 0 if c2_pixels[x, y] == 0 else 1
                
                # Coordenadas de los sub-píxeles
                col1_x = x * 2
                col2_x = x * 2 + 1

                # --- LÓGICA COLUMNA 1: EL SECRETO ---
                # Esta columna gestiona si las sombras coinciden o no para revelar el secreto.
                
                px_s1_c1 = self._get_random_color() # Sombra 1 siempre aleatoria
                
                if s == 1: # Secreto Blanco -> Sombra 2 COINCIDE con Sombra 1
                    px_s2_c1 = px_s1_c1
                else:      # Secreto Negro -> Sombra 2 DIFIERE de Sombra 1
                    px_s2_c1 = self._get_different_color(px_s1_c1)

                # --- LÓGICA COLUMNA 2: LAS CUBIERTAS ---
                # Esta columna gestiona el ruido de fondo Y la inserción de cubiertas.
                # Base: Generar ruido (colores diferentes) para que el fondo sea "gris" (mitad oscuro).
                
                base_s1_c2 = self._get_random_color()
                # Para asegurar ruido de fondo (l=1), S2 debe ser diferente a S1 en esta columna base
                base_s2_c2 = self._get_different_color(base_s1_c2) 

                # APLICAR CUBIERTAS (Override)
                # Si hay cubierta negra, FORZAMOS el pixel a Negro en esta columna.
                
                # Sombra 1, Columna 2
                if c1 == 0: # Si Cubierta 1 es negra
                    px_s1_c2 = self.BLACK
                else:
                    px_s1_c2 = base_s1_c2

                # Sombra 2, Columna 2
                if c2 == 0: # Si Cubierta 2 es negra
                    px_s2_c2 = self.BLACK
                else:
                    px_s2_c2 = base_s2_c2

                # --- ASIGNACIÓN FINAL ---
                out1_pixels[col1_x, y] = px_s1_c1
                out1_pixels[col2_x, y] = px_s1_c2
                
                out2_pixels[col1_x, y] = px_s2_c1
                out2_pixels[col2_x, y] = px_s2_c2

        return out_shadow1, out_shadow2

    def simulate_stacking(self, shadow1, shadow2):
        width, height = shadow1.size
        stacked = Image.new('RGB', (width, height))
        s1_data = shadow1.load()
        s2_data = shadow2.load()
        stacked_data = stacked.load()

        for y in range(height):
            for x in range(width):
                p1 = s1_data[x, y]
                p2 = s2_data[x, y]
                
                # Lógica física: Si alguno es negro o son diferentes colores -> NEGRO
                if p1 == self.BLACK or p2 == self.BLACK:
                    stacked_data[x, y] = self.BLACK
                elif p1 != p2: # Bloqueo de luz por colores distintos
                    stacked_data[x, y] = self.BLACK
                else: # Son iguales y tienen color -> Pasa la luz
                    stacked_data[x, y] = p1
                    
        return stacked

if __name__ == "__main__":
    try:
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        INPUT_DIR = os.path.join(BASE_DIR, "../ImagenesCreadas")
        OUTPUT_DIR = os.path.join(BASE_DIR, "../ImagenesCreadas")

        # Usa las imágenes generadas por el script "create_non_overlapping_images"
        processor = CBWEVCS_Strict()

        secret_path = os.path.join(INPUT_DIR, "secret.png")
        cover1_path = os.path.join(INPUT_DIR, "cover1.png")
        cover2_path = os.path.join(INPUT_DIR, "cover2.png")

        s1, s2 = processor.process_images(secret_path, cover1_path, cover2_path)
        
        s1.save(os.path.join(OUTPUT_DIR, "C1_shadow1.png"))
        s2.save(os.path.join(OUTPUT_DIR, "C1_shadow2.png"))
        
        final = processor.simulate_stacking(s1, s2)
        final.save(os.path.join(OUTPUT_DIR, "C1_stacked.png"))
        print("¡Listo! Revisa 'C1_stacked.png' para ver el resultado del apilamiento.")
    except Exception as e:
        print(f"Error: {e}")