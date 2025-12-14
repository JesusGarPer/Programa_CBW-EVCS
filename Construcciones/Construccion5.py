import random
import math
from PIL import Image
import os

class CBWEVCS_Construction5_PB:
    def __init__(self, n_participants):
        self.n = n_participants
        
        # Colores base
        self.RED   = (255, 0, 0)
        self.GREEN = (0, 255, 0)
        self.BLUE  = (0, 0, 255)
        self.BLACK = (0, 0, 0)
        self.BASE_COLORS = [self.RED, self.GREEN, self.BLUE]
        
        # --- EXPANSIÓN (Teorema 2 / Const 5)  ---
        # El paper define m = 2 * ceil(n/3)
        # Esto implica dos bloques de igual tamaño: ceil(n/3)
        
        self.block_size = math.ceil(self.n / 3)
        self.m = 2 * self.block_size
        
        print(f"Construcción 5 Perfect Black (n={self.n}): Expansión m={self.m} (Bloques de {self.block_size})")

    def _get_random_vector(self, length):
        """Genera un vector aleatorio de colores de longitud 'length'"""
        return [random.choice(self.BASE_COLORS) for _ in range(length)]

    def _get_balanced_shuffled_vectors(self, length):
        """
        Genera 'n' vectores para el caso SECRETO NEGRO.
        Estrategia 'Perfect Black': Intentamos que sean lo más distintos posible.
        Usamos la base cíclica R,G,B,R... y la barajamos para cada píxel.
        """
        # Creamos una lista base de colores cíclicos para cubrir los N usuarios
        # Ej n=4: [R, G, B, R]
        base_colors = []
        for i in range(self.n):
            base_colors.append(self.BASE_COLORS[i % 3])
            
        # Para cada posición del vector (ancho del bloque), barajamos esta asignación
        # Esto asegura que si User 1 tiene Rojo, User 2 probablemente tenga otro color.
        
        # Matriz temporal: n filas x length columnas
        vectors = [[None]*length for _ in range(self.n)]
        
        for k in range(length):
            # Para la columna 'k' del bloque, barajamos la asignación de colores
            col_colors = base_colors[:]
            random.shuffle(col_colors)
            
            for i in range(self.n):
                vectors[i][k] = col_colors[i]
                
        return vectors

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

        print("Procesando Construcción 5 (PB)...")

        for y in range(height):
            for x in range(width):
                s = 0 if s_pixels[x, y] == 0 else 1
                c_states = [(0 if cp[x,y] == 0 else 1) for cp in c_pixels_list]
                
                start_x = x * self.m

                # =========================================================
                # BLOQUE 1: SECRETO PERFECTO (Ancho = block_size)
                # =========================================================
                # Este bloque ocupa la primera mitad del pixel expandido
                
                if s == 1: 
                    # --- CASO BLANCO ---
                    # Todos reciben el MISMO vector aleatorio.
                    shared_vector = self._get_random_vector(self.block_size)
                    
                    for i in range(self.n):
                        for k in range(self.block_size):
                            shadow_pixels_list[i][start_x + k, y] = shared_vector[k]
                            
                else:
                    # --- CASO NEGRO ---
                    # Usamos vectores balanceados y barajados.
                    # Maximizamos la probabilidad de "choque" de colores (R vs G) -> Negro.
                    vectors = self._get_balanced_shuffled_vectors(self.block_size)
                    
                    for i in range(self.n):
                        for k in range(self.block_size):
                            shadow_pixels_list[i][start_x + k, y] = vectors[i][k]

                # =========================================================
                # BLOQUE 2: CUBIERTAS (Ancho = block_size)
                # =========================================================
                # Idéntico a Construcción 4, pero ocupando la segunda mitad
                
                offset_x = start_x + self.block_size
                
                for col_idx in range(self.block_size):
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
    # --- CONFIGURACIÓN ---
    N = 3 # Puedes probar con 3, 4, 5...

    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    INPUT_DIR = os.path.join(BASE_DIR, "../ImagenesCreadas")
    OUTPUT_DIR = os.path.join(BASE_DIR, "../ImagenesCreadas")
    
    # Usamos las imágenes B/N generadas anteriormente
    secret_file = os.path.join(INPUT_DIR, "secret.png")
    cover_files = [os.path.join(INPUT_DIR, f"cover{i+1}.png") for i in range(N)]
    
    try:
        processor = CBWEVCS_Construction5_PB(n_participants=N)
        shadows = processor.process_images(secret_file, cover_files)
        
        # Guardar sombras
        for i, s in enumerate(shadows):
            shadow_path = os.path.join(OUTPUT_DIR, f"C5_shadow{i+1}.png")
            s.save(shadow_path)
            print(f"Sombra {i+1} guardada.")
            
        # Comprobación Exhaustiva (Todos contra todos)
        for i in range(len(shadows)):
            for j in range(i + 1, len(shadows)):
                print(f"Apilando User {i+1} + User {j+1}...")
                res = processor.simulate_stacking(shadows[i], shadows[j])
                stacked_path = os.path.join(OUTPUT_DIR, f"C5_stacked_{i+1}y{j+1}.png")
                res.save(stacked_path)

        stacked_all = shadows[0]
        for i in range(1, len(shadows)):
            stacked_all = processor.simulate_stacking(stacked_all, shadows[i])
        
        stacked_all_path = os.path.join(OUTPUT_DIR, "C5_stacked_ALL.png")
        stacked_all.save(stacked_all_path)
        
        print("¡Proceso terminado! Revisa los resultados C5.")
        
    except Exception as e:
        print(f"Error: {e}")
        print("Recuerda generar las imágenes con el script anterior si cambiaste N.")