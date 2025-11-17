# sugeno_engine.py
# Orang3 (Rafly) - Sugeno Inference Engine


import numpy as np
try:
    import skfuzzy.control as ctrl
except ImportError:
    print("Library scikit-fuzzy belum diinstall.")

# --- 1. IMPORT DARI TEMAN TIM ---
try:
    # Mengambil Rule yang sudah dibuat Shaquille (Orang 2)
    from fuzzy_rules import load_all_rules
    # Mengambil Variabel Input/Output yang sudah dibuat Rian (Orang 1)
    # (Kita butuh output 'consequent' untuk defuzzification Sugeno manual jika perlu,
    # tapi scikit-fuzzy biasanya menangani Mamdani. Untuk Sugeno murni di skfuzzy
    # agak tricky, tapi ini cara standard integrasinya).
    from fuzzy_variables import antecedents, consequent
    
    IMPORTS_OK = True
except ImportError as e:
    print(f"ERROR: Gagal import file teman. {e}")
    IMPORTS_OK = False

# --- 2. MEMBUAT SISTEM KONTROL (ENGINE) ---

def build_simulation():
    
    if not IMPORTS_OK:
        return None

    print("[Sugeno Engine]: Memuat aturan dari Shaquille...")
    # 1. Ambil rules dari Shaquille
    rules_list = load_all_rules()
    
    if not rules_list:
        print("ERROR: Tidak ada rule yang dimuat.")
        return None

    print(f"[Sugeno Engine]: Berhasil memuat {len(rules_list)} aturan.")
    print("[Sugeno Engine]: Membangun ControlSystem...")

    # 2. Buat Control System
    # Ini akan menggabungkan input Rian + Rules Shaquille menjadi satu otak
    ranking_ctrl = ctrl.ControlSystem(rules_list)
    
    # 3. Buat Simulasi (Ini yang akan dipakai untuk menghitung)
    simulation = ctrl.ControlSystemSimulation(ranking_ctrl)
    
    return simulation

# Inisialisasi simulasi SEKALI saja agar cepat
# (Global variable untuk menampung mesin yang sudah jadi)
RANKING_SIMULATION = build_simulation()

# --- 3. FUNGSI UTAMA (YANG AKAN DIPANGGIL UI) ---

def get_sugeno_score(tlr_val, rpp_val, go_val, oi_val, pr_val):

    
    # Cek apakah mesin siap
    if RANKING_SIMULATION is None:
        return 0.0 # Kembalikan 0 jika sistem error

    try:
        # 1. Masukkan Input ke Mesin
        # Pastikan nama string ('TLR', dll) SAMA PERSIS dengan label di fuzzy_variables.py milik Rian
        # Asumsi Rian memberi label input sebagai: 'TLR', 'RPP', 'GO', 'OI', 'PR'
        RANKING_SIMULATION.input['TLR'] = tlr_val
        RANKING_SIMULATION.input['RPP'] = rpp_val
        RANKING_SIMULATION.input['GO']  = go_val
        RANKING_SIMULATION.input['OI']  = oi_val
        RANKING_SIMULATION.input['PR']  = pr_val

        # 2. Jalankan Perhitungan (Crunch the numbers!)
        # Di sinilah Firing Strength & Weighted Average dihitung otomatis oleh library
        RANKING_SIMULATION.compute()

        # 3. Ambil Hasilnya
        # Asumsi Rian memberi label output sebagai: 'Score'
        final_score = RANKING_SIMULATION.output['Score']
        
        return final_score

    except Exception as e:
        print(f"ERROR saat menghitung skor: {e}")
        return 0.0

# --- TESTING MANDIRI (Agar Rafly bisa tes tanpa UI) ---
if __name__ == "__main__":
    print("\n--- Test Sugeno Engine ---")
    # Tes dengan data IITM (Juara 1) dari Table 4
    # Input: 84.57, 83.54, 87.13, 66.08, 94.14
    test_score = get_sugeno_score(84.57, 83.54, 87.13, 66.08, 94.14)
    print(f"Input Data IITM -> Output Skor: {test_score}")
    
    # Tes data rendah
    test_score_low = get_sugeno_score(10, 10, 10, 10, 10)
    print(f"Input Data Rendah -> Output Skor: {test_score_low}")