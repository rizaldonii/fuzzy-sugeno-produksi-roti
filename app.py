import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# --- KONFIGURASI HALAMAN ---
st.set_page_config(
    page_title="Sistem Fuzzy Sugeno - Roti Ganda",
    page_icon="🍞",
    layout="centered"
)

# --- CSS UNTUK UI MODERN & BERSIH ---
st.markdown("""
<style>
    .result-card {
        background-color: #f8f9fa;
        border-radius: 10px;
        padding: 20px;
        text-align: center;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        margin-bottom: 20px;
    }
    .result-value {
        font-size: 48px;
        font-weight: bold;
        color: #007bff;
    }
    .result-label {
        font-size: 18px;
        color: #666;
    }
</style>
""", unsafe_allow_html=True)

# --- FUNGSI KEANGGOTAAN (MEMBERSHIP FUNCTIONS) ---
# Referensi fungsi trapesium dan segitiga [cite: 116, 123]

def trapmf(x, p):
    """Fungsi Keanggotaan Trapesium: p = [a, b, c, d]"""
    return np.maximum(0, np.minimum(np.minimum((x - p[0]) / (p[1] - p[0]), 1), (p[3] - x) / (p[3] - p[2])))

def trimf(x, p):
    """Fungsi Keanggotaan Segitiga: p = [a, b, c]"""
    return np.maximum(0, np.minimum((x - p[0]) / (p[1] - p[0]), (p[2] - x) / (p[2] - p[1])))

# --- DEFINISI VARIABEL FUZZY ---
# Parameter diambil persis dari Paper Halaman 6-7 [cite: 201, 209, 210]

# 1. Variabel Input: PERMINTAAN (Demand)
def fuzzify_permintaan(x):
    # KECIL: Trapmf [778, 975, 1030, 1310]
    u_kecil = trapmf(x, [778, 975, 1030, 1310])
    # SEDANG: Trimf [1030, 1310, 1589]
    u_sedang = trimf(x, [1030, 1310, 1589])
    # BESAR: Trapmf [1310, 1589, 1695, 1796]
    u_besar = trapmf(x, [1310, 1589, 1695, 1796])
    return u_kecil, u_sedang, u_besar

# 2. Variabel Input: PERSEDIAAN (Supply)
def fuzzify_persediaan(x):
    # SEDIKIT: Trapmf [492, 588, 607, 750]
    u_sedikit = trapmf(x, [492, 588, 607, 750])
    # SEDANG: Trimf [607, 750, 894]
    u_sedang = trimf(x, [607, 750, 894])
    # BANYAK: Trapmf [750, 894, 912, 1008]
    u_banyak = trapmf(x, [750, 894, 912, 1008])
    return u_sedikit, u_sedang, u_banyak

def get_formula_latex(x, p, label):
    """
    Menghasilkan string LaTeX berdasarkan posisi x pada kurva.
    p: list parameter [a, b, c] atau [a, b, c, d]
    label: nama himpunan (misal: 'Sedikit')
    """
    # Cek Trapesium (4 parameter)
    if len(p) == 4:
        a, b, c, d = p
        if x <= a or x >= d:
            return f"\\mu_{{{label}}}({x}) = 0 \\quad (Di luar range)"
        elif b <= x <= c:
            return f"\\mu_{{{label}}}({x}) = 1 \\quad (Di area puncak)"
        elif a < x < b:
            val = (x - a) / (b - a)
            return f"\\mu_{{{label}}}({x}) = \\frac{{x - {a}}}{{{b} - {a}}} = \\frac{{{x - a}}}{{{b - a}}} = {val:.4f}"
        elif c < x < d:
            val = (d - x) / (d - c)
            return f"\\mu_{{{label}}}({x}) = \\frac{{{d} - x}}{{{d} - {c}}} = \\frac{{{d - x}}}{{{d - c}}} = {val:.4f}"
            
    # Cek Segitiga (3 parameter)
    elif len(p) == 3:
        a, b, c = p
        if x <= a or x >= c:
            return f"\\mu_{{{label}}}({x}) = 0 \\quad (Di luar range)"
        elif x == b:
            return f"\\mu_{{{label}}}({x}) = 1 \\quad (Tepat di puncak)"
        elif a < x < b:
            val = (x - a) / (b - a)
            return f"\\mu_{{{label}}}({x}) = \\frac{{x - {a}}}{{{b} - {a}}} = \\frac{{{x - a}}}{{{b - a}}} = {val:.4f}"
        elif b < x < c:
            val = (c - x) / (c - b)
            return f"\\mu_{{{label}}}({x}) = \\frac{{{c} - x}}{{{c} - {b}}} = \\frac{{{c - x}}}{{{c - b}}} = {val:.4f}"
            
    return "Error parsing formula"

# 3. Variabel Output: PRODUKSI (Konstanta Sugeno)
# 
Z_SEDIKIT = 1996
Z_SEDANG = 2275
Z_BANYAK = 2579

# --- LOGIKA UTAMA (INFERENSI & DEFUZZIFIKASI) ---

def calculate_fuzzy_sugeno(in_minta, in_sedia):
    # 1. Fuzzifikasi
    pm_kecil, pm_sedang, pm_besar = fuzzify_permintaan(in_minta)
    ps_sedikit, ps_sedang, ps_banyak = fuzzify_persediaan(in_sedia)

    # 2. Inferensi (Rule Evaluation)
    # Berdasarkan Tabel 4 
    # Operator yang digunakan adalah MIN (AND) [cite: 156]
    
    rules = []
    
    # Rule 1: IF Minta KECIL & Sedia SEDIKIT -> Produksi SEDIKIT
    a1 = min(pm_kecil, ps_sedikit); z1 = Z_SEDIKIT
    rules.append({"Rule": 1, "Alpha": a1, "Z": z1, "Ket": "Kecil & Sedikit -> Sedikit"})
    
    # Rule 2: IF Minta KECIL & Sedia SEDANG -> Produksi SEDIKIT
    a2 = min(pm_kecil, ps_sedang); z2 = Z_SEDIKIT
    rules.append({"Rule": 2, "Alpha": a2, "Z": z2, "Ket": "Kecil & Sedang -> Sedikit"})
    
    # Rule 3: IF Minta KECIL & Sedia BANYAK -> Produksi SEDIKIT
    a3 = min(pm_kecil, ps_banyak); z3 = Z_SEDIKIT
    rules.append({"Rule": 3, "Alpha": a3, "Z": z3, "Ket": "Kecil & Banyak -> Sedikit"})
    
    # Rule 4: IF Minta SEDANG & Sedia SEDIKIT -> Produksi SEDIKIT
    a4 = min(pm_sedang, ps_sedikit); z4 = Z_SEDIKIT
    rules.append({"Rule": 4, "Alpha": a4, "Z": z4, "Ket": "Sedang & Sedikit -> Sedikit"})
    
    # Rule 5: IF Minta SEDANG & Sedia SEDANG -> Produksi SEDANG
    a5 = min(pm_sedang, ps_sedang); z5 = Z_SEDANG
    rules.append({"Rule": 5, "Alpha": a5, "Z": z5, "Ket": "Sedang & Sedang -> Sedang"})
    
    # Rule 6: IF Minta SEDANG & Sedia BANYAK -> Produksi SEDANG
    a6 = min(pm_sedang, ps_banyak); z6 = Z_SEDANG
    rules.append({"Rule": 6, "Alpha": a6, "Z": z6, "Ket": "Sedang & Banyak -> Sedang"})
    
    # Rule 7: IF Minta BESAR & Sedia SEDIKIT -> Produksi SEDIKIT
    a7 = min(pm_besar, ps_sedikit); z7 = Z_SEDIKIT
    rules.append({"Rule": 7, "Alpha": a7, "Z": z7, "Ket": "Besar & Sedikit -> Sedikit"})
    
    # Rule 8: IF Minta BESAR & Sedia SEDANG -> Produksi SEDANG
    a8 = min(pm_besar, ps_sedang); z8 = Z_SEDANG
    rules.append({"Rule": 8, "Alpha": a8, "Z": z8, "Ket": "Besar & Sedang -> Sedang"})
    
    # Rule 9: IF Minta BESAR & Sedia BANYAK -> Produksi BANYAK
    a9 = min(pm_besar, ps_banyak); z9 = Z_BANYAK
    rules.append({"Rule": 9, "Alpha": a9, "Z": z9, "Ket": "Besar & Banyak -> Banyak"})

    # 3. Defuzzifikasi (Weighted Average) [cite: 151]
    numerator = sum(r["Alpha"] * r["Z"] for r in rules)
    denominator = sum(r["Alpha"] for r in rules)
    
    if denominator == 0:
        result = 0 # Hindari pembagian dengan nol
    else:
        result = numerator / denominator
        
    return result, rules, (pm_kecil, pm_sedang, pm_besar), (ps_sedikit, ps_sedang, ps_banyak)

# --- VISUALISASI GRAFIK ---
def plot_graph(x_val, input_type):
    fig, ax = plt.subplots(figsize=(8, 3))
    
    if input_type == "minta":
        x = np.linspace(700, 1800, 500)
        y_kecil = trapmf(x, [778, 975, 1030, 1310])
        y_sedang = trimf(x, [1030, 1310, 1589])
        y_besar = trapmf(x, [1310, 1589, 1695, 1796])
        ax.plot(x, y_kecil, label='Kecil', color='green')
        ax.plot(x, y_sedang, label='Sedang', color='orange')
        ax.plot(x, y_besar, label='Besar', color='red')
        title = "Membership Function: Permintaan"
    else:
        x = np.linspace(400, 1100, 500)
        y_sedikit = trapmf(x, [492, 588, 607, 750])
        y_sedang = trimf(x, [607, 750, 894])
        y_banyak = trapmf(x, [750, 894, 912, 1008])
        ax.plot(x, y_sedikit, label='Sedikit', color='green')
        ax.plot(x, y_sedang, label='Sedang', color='orange')
        ax.plot(x, y_banyak, label='Banyak', color='red')
        title = "Membership Function: Persediaan"

    # Plot user input line
    ax.axvline(x=x_val, color='blue', linestyle='--', linewidth=2, label='Input Anda')
    
    ax.set_title(title)
    ax.legend(loc='upper right')
    ax.grid(True, linestyle=':', alpha=0.6)
    ax.set_ylim(0, 1.1)
    
    # Hide top and right spines for cleaner look
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    
    return fig

# --- UI UTAMA ---

st.title("Prediksi Produksi Roti Ganda")
st.markdown("Sistem Inferensi Fuzzy Metode Sugeno (Studi Kasus: PT Roti Ganda Siantar)")
st.markdown("---")

col1, col2 = st.columns(2)

with col1:
    st.subheader("Data Permintaan")
    # Range input disesuaikan dengan domain pada paper [cite: 183]
    input_minta = st.number_input("Jumlah Permintaan (Bungkus)", min_value=1030, max_value=1589, step=1)
    st.caption("Range domain fuzzy: 1030 - 1589")

with col2:
    st.subheader("Data Persediaan")
    # Range input disesuaikan dengan domain pada paper [cite: 183]
    input_sedia = st.number_input("Jumlah Persediaan (Bungkus)", min_value=607, max_value=894, step=1)
    st.caption("Range domain fuzzy: 607 - 894")

# Calculate
hasil_produksi, rule_data, degrees_minta, degrees_sedia = calculate_fuzzy_sugeno(input_minta, input_sedia)

st.markdown("### 🏭 Hasil Rekomendasi Produksi")
st.markdown(f"""
<div class="result-card">
    <div class="result-value">{int(hasil_produksi)}</div>
    <div class="result-label">Bungkus Roti</div>
</div>
""", unsafe_allow_html=True)

# --- BAGIAN PENJELASAN (EXPANDER) ---
with st.expander("🔍 Lihat Detail Perhitungan (Step-by-Step)"):
    st.markdown("### 1. Fuzzifikasi (Input -> Derajat Keanggotaan)")
    st.info("Rumus dipilih otomatis berdasarkan posisi nilai input pada grafik.")
    
    # --- Detail Permintaan ---
    st.markdown(f"#### A. Variabel Permintaan (Input: {input_minta})")
    st.pyplot(plot_graph(input_minta, "minta"))
    
    # Menampilkan rumus untuk Kecil, Sedang, Besar
    # Parameter harus sama persis dengan yang ada di fungsi fuzzify_permintaan
    st.latex(get_formula_latex(input_minta, [778, 975, 1030, 1310], "Kecil"))
    st.latex(get_formula_latex(input_minta, [1030, 1310, 1589], "Sedang"))
    st.latex(get_formula_latex(input_minta, [1310, 1589, 1695, 1796], "Besar"))
    
    st.markdown("---")
    
    # --- Detail Persediaan ---
    st.markdown(f"#### B. Variabel Persediaan (Input: {input_sedia})")
    st.pyplot(plot_graph(input_sedia, "sedia"))
    
    # Menampilkan rumus untuk Sedikit, Sedang, Banyak
    # Parameter harus sama persis dengan yang ada di fungsi fuzzify_persediaan
    st.latex(get_formula_latex(input_sedia, [492, 588, 607, 750], "Sedikit"))
    st.latex(get_formula_latex(input_sedia, [607, 750, 894], "Sedang"))
    st.latex(get_formula_latex(input_sedia, [750, 894, 912, 1008], "Banyak"))
    
    
    st.markdown("---")
    st.markdown("### 2. Inferensi (Evaluasi Aturan)")
    st.write("Menggunakan operator **MIN** untuk mendapatkan nilai α-predikat (Alpha) setiap aturan.")
    st.write("Nilai Z adalah konstanta Output Sugeno: **Sedikit=1996, Sedang=2275, Banyak=2579**.")
    
    # Tampilkan Tabel Aturan
    df_rules = pd.DataFrame(rule_data)
    # Highlight row where Alpha > 0
    def highlight_active(s):
        return ['background-color: #e6f3ff' if v > 0 else '' for v in s]
    
    st.dataframe(df_rules.style.apply(highlight_active, subset=['Alpha'], axis=0), use_container_width=True)

    st.markdown("---")
    st.markdown("### 3. Defuzzifikasi (Weighted Average)")
    st.write("Menghitung rata-rata tertimbang. Hanya rule dengan nilai α > 0 yang dimasukkan ke dalam perhitungan.")
    
    # Filter hanya rule yang memiliki alpha > 0 untuk ditampilkan di rumus
    active_rules = [r for r in rule_data if r["Alpha"] > 0]
    
    if len(active_rules) > 0:
        # 1. Membuat String Rumus Bagian Atas (Pembilang) -> (Alpha * Z) + ...
        # Format: (0.25 * 1996) + (0.40 * 2275)
        numerator_str = " + ".join([f"({r['Alpha']:.3f} \\times {r['Z']})" for r in active_rules])
        
        # 2. Membuat String Rumus Bagian Bawah (Penyebut) -> Alpha + ...
        # Format: 0.25 + 0.40
        denominator_str = " + ".join([f"{r['Alpha']:.3f}" for r in active_rules])
        
        # 3. Tampilkan Rumus Lengkap dengan Angka Asli
        st.markdown("**Detail Substitusi Nilai:**")
        st.latex(f"Produksi = \\frac{{{numerator_str}}}{{{denominator_str}}}")
        
        # 4. Tampilkan Hasil Kalkulasi Antara
        numerator_val = sum(r["Alpha"] * r["Z"] for r in active_rules)
        denominator_val = sum(r["Alpha"] for r in active_rules)
        
        st.latex(f"Produksi = \\frac{{{numerator_val:.4f}}}{{{denominator_val:.4f}}} = \\mathbf{{{numerator_val / denominator_val:.4f}}}")
        
    else:
        st.warning("⚠️ Tidak ada rule yang aktif (Total Alpha = 0). Input mungkin berada di luar jangkauan fuzzy yang didefinisikan.")
        st.latex(r"Produksi = 0")