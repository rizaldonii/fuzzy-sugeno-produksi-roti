# sugeno_engine.py
# Orang3 (Rafly) akan implementasikan inference Sugeno di file ini.
# Sementara, dummy agar UI tidak error saat di-run.
import numpy as np

# --- 1. MEMANGGIL MEMBERSHIP (Orang 1) ---
# Menggunakan fungsi keanggotaan segitiga (trimf) karena sederhana dan umum.
# Untuk Sugeno, output (konsekuen) adalah konstanta atau fungsi linear,
# dalam kasus ini kita asumsikan sebagai konstanta (level 1, 2, 3, 4, 5).

def trimf(x, a, b, c):
    """Fungsi Keanggotaan Segitiga (Triangular Membership Function)"""
    return np.maximum(0, np.minimum((x - a) / (b - a), (c - x) / (c - b)))

def get_membership(value):
    """Menghitung nilai keanggotaan untuk semua 5 input pada 3 level (1, 2, 3)"""
    
    # Asumsi range input adalah [0, 100] dan MFs tumpang tindih secara simetris.
    # Level 1: Rendah (Low), Level 2: Sedang (Medium), Level 3: Tinggi (High)
    
    # Definisi MFs (a, b, c):
    mf_low = lambda x: trimf(x, 0, 0, 50)
    mf_medium = lambda x: trimf(x, 0, 50, 100)
    mf_high = lambda x: trimf(x, 50, 100, 100)
    
    # Mengembalikan dict of dicts untuk mempermudah akses
    mf_values = {}
    for input_name, x in value.items():
        mf_values[input_name] = {
            1: mf_low(x),     # Level 1 (Low)
            2: mf_medium(x),  # Level 2 (Medium)
            3: mf_high(x)     # Level 3 (High)
        }
    return mf_values

# --- 2. MEMANGGIL RULES (Orang 2) & GENERATOR OTOMATIS RULE ---

def generate_rules():
    """
    Membuat generator otomatis rule Sugeno berdasarkan pola Table 3:
    5 input, 3 level per input -> 3^5 = 243 kombinasi.
    Output (konsekuen) diasumsikan sebagai level 1 hingga 5, 
    di mana 1 adalah terburuk dan 5 adalah terbaik.
    
    Asumsi untuk penentuan 'out' (dapat disesuaikan):
    out = (tlr + rpp + go + oi + pr) / 5 (lalu dibulatkan)
    
    Karena level input adalah 1, 2, 3, total minimum adalah 5 (1*5) dan 
    maksimum adalah 15 (3*5). Kita petakan ke level output 1-5.
    
    * Total 5-7  -> Output 1 (Worst)
    * Total 8-9  -> Output 2
    * Total 10   -> Output 3 (Medium)
    * Total 11-12 -> Output 4
    * Total 13-15 -> Output 5 (Best)
    """
    
    rules = []
    levels = [1, 2, 3] # Level input: Low, Medium, High
    
    for tlr in levels:
        for rpp in levels:
            for go in levels:
                for oi in levels:
                    for pr in levels:
                        # Menentukan output berdasarkan jumlah level input (Sederhana)
                        total_level = tlr + rpp + go + oi + pr
                        
                        if total_level <= 7:
                            out = 1
                        elif total_level <= 9:
                            out = 2
                        elif total_level == 10:
                            out = 3
                        elif total_level <= 12:
                            out = 4
                        else: # total_level >= 13
                            out = 5
                            
                        rule = {
                            "tlr": tlr, "rpp": rpp, "go": go, "oi": oi, "pr": pr, "out": out
                        }
                        rules.append(rule)
                        
    return rules

def get_rules():
    """Menyediakan fungsi untuk dipakai inference"""
    return generate_rules()

# Inisialisasi rules hanya sekali
RULES = get_rules()

# --- 3. MENGHITUNG FIRING STRENGTH RULE SUGENO ---

def calculate_firing_strength(mf_values, rule):
    """
    Menghitung Firing Strength (alfa) untuk satu rule Sugeno.
    Menggunakan operasi MIN (T-Norm) pada semua nilai keanggotaan anteseden.
    """
    
    # Mendapatkan nilai keanggotaan untuk kondisi anteseden (IF part) dari rule
    strength_tlr = mf_values['tlr'][rule['tlr']]
    strength_rpp = mf_values['rpp'][rule['rpp']]
    strength_go = mf_values['go'][rule['go']]
    strength_oi = mf_values['oi'][rule['oi']]
    strength_pr = mf_values['pr'][rule['pr']]
    
    # Firing Strength (alfa) adalah nilai minimum dari semua kekuatan anteseden (MIN operator)
    firing_strength = min(
        strength_tlr,
        strength_rpp,
        strength_go,
        strength_oi,
        strength_pr
    )
    
    # Untuk Sugeno ordo nol, z adalah output konstanta (rule['out'])
    z = rule['out']
    
    return firing_strength, z

# --- 4. WEIGHTED AVERAGE OUTPUT ---

def weighted_average_defuzzification(results):
    """
    Menghitung skor akhir menggunakan metode Weighted Average Defuzzification.
    Skor = Sigma(alfa_i * z_i) / Sigma(alfa_i)
    """
    
    numerator = 0  # Sigma(alfa_i * z_i)
    denominator = 0  # Sigma(alfa_i)
    
    for firing_strength, z in results:
        numerator += firing_strength * z
        denominator += firing_strength
        
    if denominator == 0:
        # Jika tidak ada rule yang terpicu, kembalikan skor default atau NaN
        return 0.0
        
    final_score = numerator / denominator
    return final_score

# --- 5. MENYEDIAKAN FUNGSI FINAL ---

def get_sugeno_score(tlr, rpp, go, oi, pr):
    """
    Fungsi utama untuk menghitung skor Sugeno
    
    Args:
        tlr (float): Teaching, Learning and Resources
        rpp (float): Research and Professional Practice
        go (float): Graduation Outcomes
        oi (float): Outreach and Inclusivity
        pr (float): Perception
        
    Returns:
        float: Skor akhir Sugeno (antara 1 dan 5, atau lebih luas)
    """
    
    # 1. Mengumpulkan input
    input_values = {
        "tlr": tlr, "rpp": rpp, "go": go, "oi": oi, "pr": pr
    }
    
    # 2. Fuzzifikasi: Hitung nilai keanggotaan untuk input
    mf_values = get_membership(input_values)
    
    # 3. Inferensi: Hitung firing strength dan output (z) untuk setiap rule
    rule_results = []
    
    for rule in RULES:
        firing_strength, z = calculate_firing_strength(mf_values, rule)
        rule_results.append((firing_strength, z))
        
    # 4. Defuzzifikasi: Hitung skor akhir menggunakan Weighted Average
    final_score = weighted_average_defuzzification(rule_results)
    
    return final_score

# --- CONTOH PENGGUNAAN ---
print(f"Total Rules yang Dibuat: {len(RULES)}") # Harusnya 243

# Contoh Kasus 1: Semua input di nilai 75 (Medium-High)
# Asumsi: input di range [0, 100]
tlr = 75
rpp = 75
go = 75
oi = 75
pr = 75

score_1 = get_sugeno_score(tlr, rpp, go, oi, pr)
print(f"\nSkor Sugeno (Input 75, 75, 75, 75, 75): {score_1:.4f}") 
# Hasil harus mendekati 4 atau 5

# Contoh Kasus 2: Semua input di nilai 25 (Low-Medium)
tlr = 25
rpp = 25
go = 25
oi = 25
pr = 25

score_2 = get_sugeno_score(tlr, rpp, go, oi, pr)
print(f"Skor Sugeno (Input 25, 25, 25, 25, 25): {score_2:.4f}")
# Hasil harus mendekati 2

# Contoh Kasus 3: Campuran
tlr = 80 # High
rpp = 10 # Low
go = 50 # Medium
oi = 90 # High
pr = 40 # Low-Medium

score_3 = get_sugeno_score(tlr, rpp, go, oi, pr)
print(f"Skor Sugeno (Input Campuran): {score_3:.4f}")
def get_sugeno_score(tlr, rpp, go, oi, pr):
    # placeholder simple — akan diganti oleh implementasi sesungguhnya
    return (tlr + rpp + go + oi + pr) / 5
