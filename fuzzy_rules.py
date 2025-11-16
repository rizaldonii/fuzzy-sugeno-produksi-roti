# fuzzy_rules.py
# Orang2 (Shaquille) akan menambahkan rule generator / rules di sini


import itertools

# 0. Import library fuzzy
try:
    from skfuzzy.control import Rule
except ImportError:
    print("FATAL ERROR: Library 'scikit-fuzzy' tidak ditemukan.")
    print("Jalankan: pip install scikit-fuzzy")
    class Rule:
        def __init__(self, *args, **kwargs):
            pass

# 1. Import dependensi dari Orang 1 
try:
    # Kita butuh variabel (antecedents) dan (consequent) dari
    from fuzzy_variables import antecedents, consequent
    IMPORTS_ORANG_1_OK = True
except ImportError:
    print("PERINGATAN: File 'fuzzy_variables.py'  belum ada.")
    IMPORTS_ORANG_1_OK = False
    antecedents, consequent = (None, None, None, None, None), None


# ==============================================================================
# --- BAGIAN 1: RULE GENERATOR (Ini yang "Menulis 243 Rule") ---
# ==============================================================================

# Definisikan nilai & bobot sesuai paper
VAL_LOW = 1
VAL_MED = 2
VAL_HIGH = 3
# Bobot: TLR(3), RP(3), GO(2), OI(1), PR(1)
# [cite_start]Sesuai [cite: 120] "weight ratio for the input parameters are 3:3:2:1:1"
WEIGHTS = [3, 3, 2, 1, 1]

def _calculate_output_level(input_combination):
    """
    Fungsi internal untuk menghitung level output (1, 2, atau 3)
    [cite_start]berdasarkan skor bobot, sesuai pola di Table 3[cite: 152].
    """
    # Menghitung skor berdasarkan bobot
    score = sum(i * w for i, w in zip(input_combination, WEIGHTS))

    # Tentukan level output (Low, Medium, High)
    # Batas ini didapat dari analisis Table 3 (misal: Rule 7 vs 8, Rule 53 vs 54)
    if score <= 12:
        return VAL_LOW
    elif score >= 21:
        return VAL_HIGH
    else:
        return VAL_MED

def _get_rules_data():
   
    print("[Rule Generator]: Menghasilkan 243 data rule...")
    all_rules_data = []
    
    # 1. Buat 3^5 = 243 kombinasi input (dari (1,1,1,1,1) ... (3,3,3,3,3))
    input_combinations = itertools.product([VAL_LOW, VAL_MED, VAL_HIGH], repeat=5)

    for combo in input_combinations:
        # combo adalah tuple input, misal: (1, 1, 1, 1, 1)
        
        # 2. Dapatkan level outputnya (1, 2, atau 3) dari kalkulator
        output_level = _calculate_output_level(combo)
        
        # 3. Simpan rule dalam format dictionary
        all_rules_data.append({
            "tlr": combo[0], "rpp": combo[1], "go": combo[2],
            "oi": combo[3], "pr": combo[4], "out": output_level
        })
            
    return all_rules_data

# ==============================================================================
# --- BAGIAN 2: RULE LOADER ---
# ==============================================================================

def load_all_rules():
    
    if not IMPORTS_ORANG_1_OK:
        print("ERROR di load_all_rules(): File 'fuzzy_variables.py' belum siap.")
        return []

    print("[Rule Loader]: Memulai proses loading 243 rules...")

    # 1. Ambil 243 data rule (dictionary) dari BAGIAN 1
    rules_data = _get_rules_data() 

    # 2. Ambil variabel fuzzy dari (Orang 1)
    tlr, rpp, go, oi, pr = antecedents
    score_output = consequent

    # 3. Kamus penerjemah
    #    (Menerjemahkan 1, 2, 3 menjadi 'Low', 'Medium', 'High')
    level_map = { 1: "Low", 2: "Medium", 3: "High" }
    final_fuzzy_rules = [] 

    # 4. Looping & Terjemahkan
    for rule_dict in rules_data:
        try:
            # Terjemahkan IF (Antecedent)
            val_tlr = level_map[rule_dict['tlr']]
            val_rpp = level_map[rule_dict['rpp']]
            val_go  = level_map[rule_dict['go']]
            val_oi  = level_map[rule_dict['oi']]
            val_pr  = level_map[rule_dict['pr']]
            
            rule_antecedent = (
                tlr[val_tlr] & rpp[val_rpp] & go[val_go] &
                oi[val_oi] & pr[val_pr]
            )
            
            # Terjemahkan THEN (Consequent)
            val_out = level_map[rule_dict['out']]
            rule_consequent = score_output[val_out]
            
            # Rakit jadi 1 Rule
            new_rule = Rule(rule_antecedent, rule_consequent)
            final_fuzzy_rules.append(new_rule)
            
        except KeyError:
            # Ini akan error jika (Orang 1) tidak memakai nama 'Low', 'Medium', 'High'
            print(f"ERROR: Pastikan menggunakan nama 'Low', 'Medium', 'High' di filenya.")
        except Exception as e:
            print(f"ERROR saat me-load rule: {e}")

    print(f"[Rule Loader]: Sukses! {len(final_fuzzy_rules)} rules berhasil di-load.")
    return final_fuzzy_rules