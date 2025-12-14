import random
from PIL import Image
import os

class CBWEVCS_Construction3:
    def __init__(self):
        # Definimos SOLO DOS colores de fondo {b1, b2} [cite: 258]
        # Usaremos el par de alto contraste (Cian, Rojo) 
        self.CYAN = (0, 255, 255)
        self.RED  = (255, 0, 0)
        self.BLACK = (0, 0, 0)
        
        # Nuestro universo de colores es binario: O es Cian, O es Rojo.
        self.PAIR = [self.CYAN, self.RED]

    def _get_random_pair_color(self):
        """Elige aleatoriamente uno de los dos colores."""
        return random.choice(self.PAIR)

    def _get_other_color(self, color):
        """
        Dado uno de los colores del par, devuelve EL OTRO.
        Al solo haber 2 opciones, esto es determinista.
        """
        if color == self.CYAN:
            return self.RED
        else:
            return self.CYAN

    def process_images(self, secret_path, cover1_path, cover2_path):
        # Cargar imágenes (B/N estricto)
        secret_img = Image.open(secret_path).convert('1')
        cover1_img = Image.open(cover1_path).convert('1')
        cover2_img = Image.open(cover2_path).convert('1')

        width, height = secret_img.size
        cover1_img = cover1_img.resize((width, height))
        cover2_img = cover2_img.resize((width, height))

        # Expansión m=2
        out_shadow1 = Image.new('RGB', (width * 2, height))
        out_shadow2 = Image.new('RGB', (width * 2, height))
        
        s_pixels = secret_img.load()
        c1_pixels = cover1_img.load()
        c2_pixels = cover2_img.load()
        out1_pixels = out_shadow1.load()
        out2_pixels = out_shadow2.load()

        print("Generando Construcción 3 (Par Cian/Rojo)...")

        for y in range(height):
            for x in range(width):
                s = 0 if s_pixels[x, y] == 0 else 1
                c1 = 0 if c1_pixels[x, y] == 0 else 1
                c2 = 0 if c2_pixels[x, y] == 0 else 1
                
                col1_x = x * 2
                col2_x = x * 2 + 1

                # --- LÓGICA CONSTRUCCIÓN 3 ---
                # Sigue la Ecuación (2) pero restringida a {b1, b2} [cite: 260]

                # COLUMNA 1: EL SECRETO
                # ---------------------
                # Elegimos color inicial para S1 (Aleatorio entre Cian/Rojo)
                px_s1_c1 = self._get_random_pair_color()
                
                if s == 1: 
                    # Secreto Blanco -> Sombra 2 IGUAL a Sombra 1
                    px_s2_c1 = px_s1_c1
                else:      
                    # Secreto Negro -> Sombra 2 es el OTRO color
                    px_s2_c1 = self._get_other_color(px_s1_c1)

                # COLUMNA 2: LAS CUBIERTAS (Y EL RUIDO DE FONDO)
                # ----------------------------------------------
                # Definimos una base para el ruido.
                base_s1_c2 = self._get_random_pair_color()
                
                # Para mantener el fondo "gris" (ruido visual equilibrado),
                # si el secreto es blanco, en la columna 2 conviene alternar colores.
                # (Lógica derivada de mantener la densidad visual).
                
                # Si S=1 (Blanco), Col 1 es transparente. Necesitamos que Col 2 sea oscura (ruido).
                # Cian + Rojo = Negro (Bloqueo).
                base_s2_c2 = self._get_other_color(base_s1_c2)

                # Si S=0 (Negro), Col 1 ya es oscura (Cian+Rojo). 
                # Col 2 también debería ser oscura para máxima negrura.
                if s == 0:
                    base_s2_c2 = self._get_other_color(base_s1_c2)

                # --- APLICAR MÁSCARAS DE CUBIERTA ---
                # Si cubierta es negra, forzamos NEGRO puro.
                
                # Sombra 1
                if c1 == 0:
                    px_s1_c2 = self.BLACK
                else:
                    px_s1_c2 = base_s1_c2

                # Sombra 2
                if c2 == 0:
                    px_s2_c2 = self.BLACK
                else:
                    px_s2_c2 = base_s2_c2

                # Asignar
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
                
                # Reglas de física de luz para Construcción 3:
                # 1. El negro bloquea todo.
                if p1 == self.BLACK or p2 == self.BLACK:
                    stacked_data[x, y] = self.BLACK
                # 2. Colores iguales pasan (Cian+Cian=Cian, Rojo+Rojo=Rojo)
                elif p1 == p2:
                    stacked_data[x, y] = p1
                # 3. Colores diferentes bloquean (Cian+Rojo = Negro)
                # Al ser un par complementario de alto contraste, actúan como negro.
                else:
                    stacked_data[x, y] = self.BLACK
                    
        return stacked

if __name__ == "__main__":
    try:
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        INPUT_DIR = os.path.join(BASE_DIR, "../ImagenesCreadas")
        OUTPUT_DIR = os.path.join(BASE_DIR, "../ImagenesCreadas")

        # Asegúrate de usar imágenes B/N (secret.png, cover1.png, cover2.png)
        processor = CBWEVCS_Construction3()

        secret_path = os.path.join(INPUT_DIR, "secret.png")
        cover1_path = os.path.join(INPUT_DIR, "cover1.png")
        cover2_path = os.path.join(INPUT_DIR, "cover2.png")

        s1, s2 = processor.process_images(secret_path, cover1_path, cover2_path)
        
        s1.save("C3_shadow1.png")
        s2.save("C3_shadow2.png")
        
        s1.save(os.path.join(OUTPUT_DIR, "C3_shadow1.png"))
        s2.save(os.path.join(OUTPUT_DIR, "C3_shadow2.png"))
        
        final = processor.simulate_stacking(s1, s2)
        final.save(os.path.join(OUTPUT_DIR, "C3_stacked.png"))
        print("¡Hecho! Construcción 3 (Cian/Rojo) generada.")
        print("Observa cómo las sombras solo tienen 2 colores (+ negro).")
    except Exception as e:
        print(f"Error: {e}")