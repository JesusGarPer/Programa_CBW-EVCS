import random
import itertools
import math
import os
from PIL import Image

# ==========================================
# CONFIGURACIÓN
# ==========================================
K_REQUIRED = 3      # Umbral
N_PARTICIPANTS = 4  # Total participantes

# Calidad de la cubierta (Mayor número = Cubierta más nítida, imagen más ancha)
COVER_REPETITION = 3 
# ==========================================

class CBWEVCS_Universal_Kn_HighQuality:
    def __init__(self, k, n, d=1):
        self.k = k
        self.n = n
        self.d = d
        
        self.RED   = (255, 0, 0)
        self.GREEN = (0, 255, 0)
        self.BLUE  = (0, 0, 255)
        self.BLACK = (0, 0, 0)
        self.TRIAD = [self.RED, self.GREEN, self.BLUE]
        
        # --- 1. MATRICES BASE (B/N) ---
        print(f"Calculando matrices combinatorias para ({self.k}, {self.n})...")
        
        # Generar todas las combinaciones de K bits
        all_k_bits = list(itertools.product([0, 1], repeat=self.k))
        block_cols_white = [list(b) for b in all_k_bits if sum(b)%2==0]
        block_cols_black = [list(b) for b in all_k_bits if sum(b)%2!=0]
        
        # Distribuir en N participantes
        subsets = list(itertools.combinations(range(self.n), self.k))
        
        self.final_cols_white = []
        self.final_cols_black = []
        
        for subset_indices in subsets:
            for col_bits in block_cols_white:
                full_col = [0] * self.n
                for idx, bit in zip(subset_indices, col_bits): full_col[idx] = bit
                self.final_cols_white.append(full_col)
            for col_bits in block_cols_black:
                full_col = [0] * self.n
                for idx, bit in zip(subset_indices, col_bits): full_col[idx] = bit
                self.final_cols_black.append(full_col)

        # --- 2. EXPANSIÓN ---
        self.raw_cols = len(self.final_cols_white)
        self.padding = (3 - (self.raw_cols % 3)) % 3
        self.filler_col = [1] * self.n 
        
        self.m_secret = (self.raw_cols + self.padding) // 3
        self.m_cover_base = math.ceil(self.n / 3)
        self.m_cover_total = self.m_cover_base * self.d
        self.m = self.m_secret + self.m_cover_total
        
        print(f" -> Matriz Base: {self.raw_cols} columnas.")
        print(f" -> m_secret: {self.m_secret} px | m_cover: {self.m_cover_total} px")
        print(f" -> ANCHO TOTAL: x{self.m} (Expansión)")

    def _generate_secret_pixels(self, is_secret_white):
        cols = self.final_cols_white[:] if is_secret_white else self.final_cols_black[:]
        for _ in range(self.padding): cols.append(self.filler_col)
        random.shuffle(cols)
        
        user_pixels = [[None]*self.m_secret for _ in range(self.n)]
        for p_idx in range(self.m_secret):
            c_r, c_g, c_b = cols[p_idx*3], cols[p_idx*3+1], cols[p_idx*3+2]
            for u in range(self.n):
                r = 0 if c_r[u] == 1 else 255
                g = 0 if c_g[u] == 1 else 255
                b = 0 if c_b[u] == 1 else 255
                user_pixels[u][p_idx] = (r, g, b)
        return user_pixels

    def process_images(self, secret_path, cover_paths):
        if len(cover_paths) != self.n: 
            print(f"Error: Faltan cubiertas. Se esperan {self.n}.")
            return []
        try:
            secret_img = Image.open(secret_path).convert('1')
            covers = [Image.open(p).convert('1') for p in cover_paths]
        except FileNotFoundError: 
            print("Error: No se encuentran las imágenes (secret.png o covers).")
            return []
        
        width, height = secret_img.size
        covers = [c.resize((width, height)) for c in covers]
        shadows = [Image.new('RGB', (width * self.m, height)) for _ in range(self.n)]
        
        s_pixels = secret_img.load()
        c_pixels_list = [c.load() for c in covers]
        shadow_pixels_list = [s.load() for s in shadows]

        print("Generando sombras...")

        for y in range(height):
            for x in range(width):
                s = 0 if s_pixels[x, y] == 0 else 1
                c_states = [(0 if cp[x,y] == 0 else 1) for cp in c_pixels_list]
                start_x = x * self.m

                # BLOQUE SECRETO
                pixels_block = self._generate_secret_pixels(s==1)
                for i in range(self.n):
                    for k in range(self.m_secret):
                        shadow_pixels_list[i][start_x + k, y] = pixels_block[i][k]

                # BLOQUE CUBIERTA (Con repetición d)
                offset_x = start_x + self.m_secret
                for col_idx in range(self.m_cover_total):
                    base_idx = col_idx % self.m_cover_base
                    group_start = base_idx * 3
                    for i in range(self.n):
                        pixel_val = self.BLACK
                        if group_start <= i < group_start + 3:
                            if c_states[i] == 0: pixel_val = self.BLACK
                            else: pixel_val = self.TRIAD[i % 3]
                        else:
                            pixel_val = self.BLACK
                        shadow_pixels_list[i][offset_x + col_idx, y] = pixel_val

        return shadows

    def simulate_stacking(self, shadows_to_stack):
        w, h = shadows_to_stack[0].size
        stacked = Image.new('RGB', (w, h))
        data_list = [s.load() for s in shadows_to_stack]
        ds = stacked.load()
        for y in range(h):
            for x in range(w):
                cur_r, cur_g, cur_b = 255, 255, 255
                for data in data_list:
                    r, g, b = data[x, y]
                    cur_r &= r; cur_g &= g; cur_b &= b
                ds[x, y] = (cur_r, cur_g, cur_b)
        return stacked

if __name__ == "__main__":

    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    INPUT_DIR = os.path.join(BASE_DIR, "../ImagenesCreadas")
    OUTPUT_DIR = os.path.join(BASE_DIR, "../ImagenesCreadas")

    secret_file = os.path.join(INPUT_DIR, "secret.png")
    cover_files = [os.path.join(INPUT_DIR, f"cover{i+1}.png") for i in range(N_PARTICIPANTS)]
    
    try:
        processor = CBWEVCS_Universal_Kn_HighQuality(k=K_REQUIRED, n=N_PARTICIPANTS, d=COVER_REPETITION)
        shadows = processor.process_images(secret_file, cover_files)
        
        if shadows:
            # 1. Guardar sombras
            for i, s in enumerate(shadows): 
                shadow_path = os.path.join(OUTPUT_DIR, f"Shadow_Final_User{i+1}.png")
                s.save(shadow_path)
            print("Sombras individuales guardadas.")

            # --- FASE DE PRUEBAS ---

            # 2. PRUEBA DE SEGURIDAD: Apilar k-1 (NO DEBE VERSE)
            # Para (4,5), apilamos 3 sombras.
            num_stack = K_REQUIRED - 1
            print(f"\n[1/3] Prueba de SEGURIDAD: Apilando {num_stack} sombras...")
            subset_fail = shadows[:num_stack] 
            res_fail = processor.simulate_stacking(subset_fail)
            filename_fail = f"Test_Security_{num_stack}_of_{N_PARTICIPANTS}.png"
            filepath_fail = os.path.join(OUTPUT_DIR, filename_fail)
            res_fail.save(filepath_fail)
            print(f" -> Resultado guardado en: {filename_fail} (Debe ser RUIDO)")

            # 3. PRUEBA DE ÉXITO: Apilar k (DEBE VERSE)
            # Para (4,5), apilamos 4 sombras.
            print(f"\n[2/3] Prueba de ÉXITO: Apilando {K_REQUIRED} sombras...")
            subset_success = shadows[:K_REQUIRED] 
            res_success = processor.simulate_stacking(subset_success)
            filename_success = f"Test_Success_{K_REQUIRED}_of_{N_PARTICIPANTS}.png"
            filepath_success = os.path.join(OUTPUT_DIR, filename_success)
            res_success.save(filepath_success)
            print(f" -> Resultado guardado en: {filename_success} (Debe verse SECRETO)")

            # 4. PRUEBA TOTAL: Apilar n (SOLO SI n > k)
            if N_PARTICIPANTS > K_REQUIRED:
                print(f"\n[3/3] Prueba TOTAL: Apilando {N_PARTICIPANTS} sombras...")
                res_all = processor.simulate_stacking(shadows)
                filename_all = f"Test_ALL_{N_PARTICIPANTS}_of_{N_PARTICIPANTS}.png"
                filepath_all = os.path.join(OUTPUT_DIR, filename_all)
                res_all.save(filepath_all)
                print(f" -> Resultado guardado en: {filename_all} (Debe verse SECRETO)")
            
    except Exception as e:
        print(f"Error crítico: {e}")
        print("¿Tienes las imágenes 'secret.png' y 'cover1...cover5.png'?")