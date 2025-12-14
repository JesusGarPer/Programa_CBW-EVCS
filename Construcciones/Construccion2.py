import random
from PIL import Image
import os

class CBWEVCS_Construction2:
    def __init__(self):
        # 1. Definir colores extendidos (RGB + CMY) [cite: 246-247]
        self.RED     = (255, 0, 0)
        self.GREEN   = (0, 255, 0)
        self.BLUE    = (0, 0, 255)
        self.CYAN    = (0, 255, 255)
        self.MAGENTA = (255, 0, 255)
        self.YELLOW  = (255, 255, 0)
        self.BLACK   = (0, 0, 0)
        
        # Lista completa S(1)
        self.COLORS = [self.RED, self.GREEN, self.BLUE, self.CYAN, self.MAGENTA, self.YELLOW]
        
        # 2. Mapa de Complementarios para la lógica de Construcción 2
        # Rojo <-> Cian, Verde <-> Magenta, Azul <-> Amarillo
        self.COMPLEMENTS = {
            self.RED: self.CYAN,
            self.CYAN: self.RED,
            self.GREEN: self.MAGENTA,
            self.MAGENTA: self.GREEN,
            self.BLUE: self.YELLOW,
            self.YELLOW: self.BLUE,
            self.BLACK: self.BLACK # El complementario de negro se trata como negro en este contexto lógico
        }

    def _get_random_color(self):
        """Elige un color aleatorio de S(1)"""
        return random.choice(self.COLORS)

    def _get_complementary(self, color):
        """Devuelve el color complementario (s barra) según el paper"""
        return self.COMPLEMENTS.get(color, self.BLACK)

    def process_images(self, secret_path, cover1_path, cover2_path):
        # Cargar imágenes
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

        print("Procesando Construcción 2 (Colores Complementarios)...")

        for y in range(height):
            for x in range(width):
                s = 0 if s_pixels[x, y] == 0 else 1
                c1 = 0 if c1_pixels[x, y] == 0 else 1
                c2 = 0 if c2_pixels[x, y] == 0 else 1
                
                col1_x = x * 2
                col2_x = x * 2 + 1

                # --- LÓGICA DE CONSTRUCCIÓN 2 (Eq. 3) ---

                # COLUMNA 1 (Se encarga del Secreto)
                # Elegimos un color aleatorio para S1
                px_s1_c1 = self._get_random_color()
                
                if s == 1: 
                    # Secreto Blanco -> Sombra 2 IGUAL a Sombra 1
                    px_s2_c1 = px_s1_c1
                else:      
                    # Secreto Negro -> Sombra 2 es COMPLEMENTARIA a Sombra 1 [cite: 249-250]
                    # Antes usábamos "random different", ahora usamos "complement"
                    px_s2_c1 = self._get_complementary(px_s1_c1)

                # COLUMNA 2 (Se encarga de las Cubiertas/Fondo)
                
                # Base: Generamos ruido usando la lógica del secreto para mantener consistencia
                base_s1_c2 = self._get_random_color()
                
                # Para el fondo (ruido), necesitamos que al apilarse se vea oscuro (gris).
                # En la Construcción 2, el fondo (secreto blanco) se genera haciendo que
                # los píxeles sean IGUALES. Pero para que las cubiertas se escondan,
                # necesitamos seguir la lógica estricta de "Si cubierta negra -> Pixel Negro".
                
                # El paper en Eq (3) Caso 1 (blanco/blanco) pone:
                # a_21 = complement(a_11)  <-- OJO: El paper usa complementos para la matriz NEGRA
                # Vamos a usar la lógica de columnas estricta nuevamente:
                
                # Si el secreto es blanco, en la col 2 queremos que se vea "ruido" 
                # para ocultar la cubierta.
                
                # Definimos el comportamiento base de la columna 2:
                if s == 1:
                    base_s2_c2 = base_s1_c2 # Coinciden (Luz) -> Fondo claro
                    # PERO, para ocultar la cubierta (que es negra), necesitamos que el fondo 
                    # tenga cierta textura.
                    # En la C2, el paper usa a_21 = complement(a_11) en la matriz base negra.
                    
                    # Vamos a simplificar con la regla que funcionó:
                    # Fondo = Ruido (Diferentes/Complementarios)
                    base_s2_c2 = self._get_complementary(base_s1_c2)
                else:
                    # Secreto Negro
                    base_s2_c2 = self._get_complementary(base_s1_c2)

                # --- APLICACIÓN DE CUBIERTAS (Override) ---
                # Esto es idéntico a C1: Si cubierta es negra, pixel es negro.
                
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
                
                # En simulación RGB, dos colores complementarios (ej. Rojo + Cian) 
                # no hacen negro automáticamente en suma aditiva digital simple,
                # pero en la lógica de transparencias (sustractiva/filtros) SÍ bloquean todo el espectro.
                # Rojo deja pasar solo R. Cian deja pasar G y B. 
                # Rojo + Cian = Bloqueo total (Negro).
                
                if p1 == self.BLACK or p2 == self.BLACK:
                    stacked_data[x, y] = self.BLACK
                elif p1 == p2:
                    stacked_data[x, y] = p1
                else:
                    # Asumimos bloqueo ideal: cualquier diferencia bloquea luz
                    # O específicamente si son complementarios
                    stacked_data[x, y] = self.BLACK 
                    
        return stacked

if __name__ == "__main__":
    try:
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        INPUT_DIR = os.path.join(BASE_DIR, "../ImagenesCreadas")
        OUTPUT_DIR = os.path.join(BASE_DIR, "../ImagenesCreadas")

        # Usa las mismas imágenes de entrada
        processor = CBWEVCS_Construction2()

        secret_path = os.path.join(INPUT_DIR, "secret.png")
        cover1_path = os.path.join(INPUT_DIR, "cover1.png")
        cover2_path = os.path.join(INPUT_DIR, "cover2.png")

        s1, s2 = processor.process_images(secret_path, cover1_path, cover2_path)
        
        s1.save(os.path.join(OUTPUT_DIR, "C2_shadow1.png"))
        s2.save(os.path.join(OUTPUT_DIR, "C2_shadow2.png"))
        
        final = processor.simulate_stacking(s1, s2)
        final.save(os.path.join(OUTPUT_DIR, "C2_stacked.png"))
        print("¡Listo! Revisa 'C2_stacked.png' para ver el resultado del apilamiento.")
    except Exception as e:
        print(f"Error: {e}")