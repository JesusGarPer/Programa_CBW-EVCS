import random
import math
import itertools
from PIL import Image
import os

class CBWEVCS_Construction4_Secure:
    def __init__(self, n_participants):
        self.n = n_participants
        
        # Colores base
        self.RED   = (255, 0, 0)
        self.GREEN = (0, 255, 0)
        self.BLUE  = (0, 0, 255)
        self.BLACK = (0, 0, 0)
        self.BASE_COLORS = [self.RED, self.GREEN, self.BLUE]
        
        # --- EXPANSIÓN (Teorema 2) ---
        self.m1 = math.ceil(math.log(self.n, 3)) if self.n > 1 else 1
        self.m2 = math.ceil(self.n / 3)
        self.m = self.m1 + self.m2
        
        print(f"Construcción 4 Segura (n={self.n}): Expansión m={self.m}")

        # Generamos TODOS los vectores posibles de longitud m1
        # Ej: Para n=3, m1=1 -> [(R), (G), (B)]
        self.all_vectors = list(itertools.product(self.BASE_COLORS, repeat=self.m1))

    def _get_random_vector(self):
        """Devuelve un vector de color aleatorio"""
        return random.choice(self.all_vectors)

    def _get_shuffled_distribution(self):
        """
        Devuelve una lista de 'n' vectores DISTINTOS barajados.
        Esto es para el caso SECRETO NEGRO.
        """
        # Seleccionamos 'n' vectores distintos al azar de los disponibles
        # Nota: Para n=3, m1=1, tomamos los 3 colores (R,G,B) y los barajamos.
        # Si n < 3^m1, tomamos una muestra aleatoria.
        selected = random.sample(self.all_vectors, self.n)
        return selected

    def process_images(self, secret_path, cover_paths):
        if len(cover_paths) != self.n:
            print(f"Error: Se requieren {self.n} cubiertas.")
            return []

        # Cargar imágenes (B/N)
        secret_img = Image.open(secret_path).convert('1')
        covers = [Image.open(p).convert('1') for p in cover_paths]
        
        width, height = secret_img.size
        covers = [c.resize((width, height)) for c in covers]

        # Lienzos de salida
        shadows = [Image.new('RGB', (width * self.m, height)) for _ in range(self.n)]
        
        s_pixels = secret_img.load()
        c_pixels_list = [c.load() for c in covers]
        shadow_pixels_list = [s.load() for s in shadows]

        print("Procesando con permutación aleatoria (Seguridad V-2)...")

        for y in range(height):
            for x in range(width):
                s = 0 if s_pixels[x, y] == 0 else 1 # 0=Negro, 1=Blanco
                c_states = [(0 if cp[x,y] == 0 else 1) for cp in c_pixels_list]
                
                start_x = x * self.m

                # =========================================================
                # PARTE 1: BLOQUE DEL SECRETO (Ancho m1) - ¡CORREGIDO!
                # =========================================================
                
                if s == 1: 
                    # --- CASO BLANCO (Transparente) ---
                    # Elegimos UN vector aleatorio.
                    # TODOS los usuarios reciben ESE MISMO vector.
                    # Al apilar: Vector A + Vector A = Vector A (Se ve color/luz).
                    shared_vector = self._get_random_vector()
                    
                    for i in range(self.n):
                        for k in range(self.m1):
                            shadow_pixels_list[i][start_x + k, y] = shared_vector[k]
                            
                else:
                    # --- CASO NEGRO (Opaco) ---
                    # Obtenemos 'n' vectores DISTINTOS y BARAJADOS.
                    # Cada usuario recibe uno diferente.
                    # Al apilar: Vector A + Vector B = Negro (Bloqueo).
                    # SEGURIDAD: Como barajamos, el Usuario 1 recibe un color aleatorio.
                    # No puede distinguir si recibió este color porque era "caso blanco" 
                    # o "caso negro". ¡Esto oculta el secreto!
                    
                    dist_vectors = self._get_shuffled_distribution()
                    
                    for i in range(self.n):
                        my_vector = dist_vectors[i]
                        for k in range(self.m1):
                            shadow_pixels_list[i][start_x + k, y] = my_vector[k]

                # =========================================================
                # PARTE 2: BLOQUE DE CUBIERTAS (Ancho m2)
                # =========================================================
                offset_x = start_x + self.m1
                
                for col_idx in range(self.m2):
                    group_start = col_idx * 3
                    
                    for i in range(self.n):
                        pixel_val = self.BLACK 
                        
                        if group_start <= i < group_start + 3:
                            if c_states[i] == 0: # Cubierta Negra
                                pixel_val = self.BLACK
                            else: # Cubierta Blanca -> Color cíclico
                                color_pos = i % 3
                                pixel_val = self.BASE_COLORS[color_pos]
                        
                        shadow_pixels_list[i][offset_x + col_idx, y] = pixel_val

        return shadows

    def simulate_stacking(self, shadow_a, shadow_b):
        w, h = shadow_a.size
        stacked = Image.new('RGB', (w, h))
        da = shadow_a.load()
        db = shadow_b.load()
        ds = stacked.load()
        
        for y in range(h):
            for x in range(w):
                pa = da[x, y]
                pb = db[x, y]
                if pa == self.BLACK or pb == self.BLACK:
                    ds[x, y] = self.BLACK
                elif pa == pb:
                    ds[x, y] = pa
                else:
                    ds[x, y] = self.BLACK
        return stacked

if __name__ == "__main__":
    N = 3 # Número de participantes (AJUSTAR SEGÚN NECESIDAD)

    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    INPUT_DIR = os.path.join(BASE_DIR, "../ImagenesCreadas")
    OUTPUT_DIR = os.path.join(BASE_DIR, "../ImagenesCreadas")

    secret_file = os.path.join(INPUT_DIR, "secret.png")
    cover_files = [os.path.join(INPUT_DIR, f"cover{i+1}.png") for i in range(N)]
    
    try:
        processor = CBWEVCS_Construction4_Secure(n_participants=N)
        shadows = processor.process_images(secret_file, cover_files)
        
        # 1. Guardar sombras
        for i, s in enumerate(shadows):
            shadow_path = os.path.join(OUTPUT_DIR, f"C4_shadow{i+1}.png")
            s.save(shadow_path)
            print(f"Guardada Sombra {i+1}")
            
        # 2. Simular apilamiento
        for i in range(len(shadows)):
            for j in range(i + 1, len(shadows)):
                print(f"Apilando User {i+1} + User {j+1}...")
                res = processor.simulate_stacking(shadows[i], shadows[j])
                stacked_path = os.path.join(OUTPUT_DIR, f"C4_stacked_{i+1}y{j+1}.png")
                res.save(stacked_path)

        stacked_all = shadows[0]
        for i in range(1, len(shadows)):
            stacked_all = processor.simulate_stacking(stacked_all, shadows[i])
        
        stacked_all_path = os.path.join(OUTPUT_DIR, "C4_stacked_ALL.png")
        stacked_all.save(stacked_all_path)
        
        print("¡Listo! Revisa 'C4_stacked.png' para ver el resultado del apilamiento.")
        
    except Exception as e:
        print(f"Error: {e}")