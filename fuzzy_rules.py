# fuzzy_rules.py
# Orang2 (Shaquille) akan menambahkan rule generator / rules di sini


# 0. Import library fuzzy
try:
    from skfuzzy.control import Rule
except ImportError:
    # Ini akan error jika scikit-fuzzy belum di-install
    # Jalankan: pip install scikit-fuzzy
    print("FATAL ERROR: Library 'scikit-fuzzy' tidak ditemukan.")
    print("Jalankan: pip install scikit-fuzzy")
    # Definisikan class bohongan agar file bisa di-import tanpa crash
    class Rule:
        def __init__(self, *args, **kwargs):
            pass

# 1. Import dependensi dari Orang 1 (fuzzy_variables.py)
try:
    # Kita butuh 2 hal dari Orang 1:
    # 1. antecedents: Tuple berisi 5 variabel input (tlr, rpp, go, oi, pr)
    # 2. consequent: 1 variabel output (score_output)
    from fuzzy_variables import antecedents, consequent
    IMPORTS_ORANG_1_OK = True
except ImportError:
    print("PERINGATAN: File 'fuzzy_variables.py' (Orang 1) belum ada atau belum siap.")
    IMPORTS_ORANG_1_OK = False
    # Definisikan variabel bohongan agar file ini tetap bisa dites
    antecedents, consequent = (None, None, None, None, None), None

# 2. Import dependensi dari Orang 3 (sugeno_engine.py)
try:
    # Kita butuh 1 fungsi dari Orang 3:
    # 1. get_rules: Fungsi yang mengembalikan list 243 dictionary
    from sugeno_engine import get_rules
    IMPORTS_ORANG_3_OK = True
except ImportError:
    print("PERINGATAN: File 'sugeno_engine.py' (Orang 3) belum ada atau belum siap.")
    IMPORTS_ORANG_3_OK = False
    # Definisikan fungsi bohongan agar file ini tetap bisa dites
    def get_rules():
        print("-> Memakai fungsi get_rules() bohongan.")
        # Mengembalikan 1 rule bohongan untuk tes
        return [{"tlr":1, "rpp":1, "go":1, "oi":1, "pr":1, "out":1}]

# ==============================================================================
# --- FUNGSI UTAMA (Rule Loader) ---
# ==============================================================================

def load_all_rules():
    """
    Fungsi ini adalah inti tugas Orang 2 (Rule Loader).
    
    1. Memanggil get_rules() dari Orang 3 untuk dapat 243 data dict.
    2. Mengambil variabel fuzzy (TLR, RPP, dll) dari Orang 1.
    3. Menggabungkan keduanya untuk menghasilkan 243 objek skfuzzy.Rule.
    
    Fungsi ini akan dipanggil oleh Orang 3.
    """
    
    # Cek apakah file dependensi sudah siap
    if not IMPORTS_ORANG_1_OK or not IMPORTS_ORANG_3_OK:
        print("ERROR di load_all_rules(): File dari Orang 1 atau Orang 3 belum siap.")
        return []

    print("[Rule Loader]: Memulai proses loading 243 rules...")

    # --- Persiapan ---
    
    # 1. Ambil 243 data rule (dictionary) dari Orang 3
    rules_data = get_rules() # Ini adalah list of dictionaries

    # 2. Ambil variabel fuzzy dari Orang 1
    tlr, rpp, go, oi, pr = antecedents
    score_output = consequent

    # 3. Buat "kamus" penerjemah
    #    Data dari Org 3: 1, 2, 3
    #    Variabel dari Org 1: 'Low', 'Medium', 'High'
    #
    # PENTING: Pastikan string 'Low', 'Medium', 'High' SAMA PERSIS
    # dengan yang didefinisikan oleh Orang 1 di file fuzzy_variables.py
    level_map = {
        1: "Low",
        2: "Medium",
        3: "High"
    }

    final_fuzzy_rules = [] # List untuk menampung 243 objek Rule

    # --- Proses Loop (Menerjemahkan) ---
    for rule_dict in rules_data:
        try:
            # --- Bagian 1: Terjemahkan IF (Antecedent) ---
            # Ambil nilai input dari data dictionary
            val_tlr = level_map[rule_dict['tlr']] 
            val_rpp = level_map[rule_dict['rpp']] 
            val_go  = level_map[rule_dict['go']]  
            val_oi  = level_map[rule_dict['oi']]  
            val_pr  = level_map[rule_dict['pr']]  
            
            # Buat antecedent (IF... AND... AND...)
            # Ini menggunakan variabel dari Orang 1
            rule_antecedent = (
                tlr[val_tlr] &
                rpp[val_rpp] &
                go[val_go] &
                oi[val_oi] &
                pr[val_pr]
            )
            
            # --- Bagian 2: Terjemahkan THEN (Consequent) ---
            val_out = level_map[rule_dict['out']] 
            
            # Buat consequent (THEN...)
            rule_consequent = score_output[val_out]
            
            # --- Bagian 3: Buat Objek Rule ---
            new_rule = Rule(rule_antecedent, rule_consequent)
            final_fuzzy_rules.append(new_rule)
            
        except KeyError as e:
            print(f"ERROR: Terjadi kesalahan mapping. Mungkin Orang 3 mengirim angka selain 1, 2, 3? {e}")
        except Exception as e:
            print(f"ERROR saat membuat rule: {e}")

    print(f"[Rule Loader]: Sukses! {len(final_fuzzy_rules)} rules berhasil di-load ke sistem.")
    
    # Kembalikan list berisi 243 objek skfuzzy.Rule
    return final_fuzzy_rules

# ==============================================================================
# --- Blok Testing (untuk Anda tes file ini secara mandiri) ---
# ==============================================================================

if __name__ == "__main__":
    # Blok ini HANYA akan jalan jika Anda me-run file ini langsung
    # >> python fuzzy_rules.py
    
    print("-----------------------------------------------------")
    print("--- Menjalankan fuzzy_rules.py sebagai script utama (Mode Tes) ---")
    print("-----------------------------------------------------")
    
    # Coba panggil fungsi utama Anda
    # Ini mungkin akan menampilkan PERINGATAN jika file 
    # 'fuzzy_variables.py' dan 'sugeno_engine.py' belum ada.
    # Itu SANGAT NORMAL.
    
    my_rules_list = load_all_rules()
    
    print("-----------------------------------------------------")
    if my_rules_list:
        print(f"Hasil Tes: Berhasil me-load {len(my_rules_list)} rule.")
        print("Contoh rule pertama yang di-load:")
        print(my_rules_list[0])
    else:
        print("Hasil Tes: Gagal me-load rules (ini wajar jika file lain belum siap).")
    
    print("--- Tes Selesai ---")