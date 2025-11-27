import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# --- 1. KONFIGURASI HALAMAN ---
st.set_page_config(
    page_title="Sistem Fuzzy Sugeno - Roti Ganda",
    page_icon="🍞",
    layout="wide"
)

# --- 2. CSS UNTUK PERCANTIK TAMPILAN ---
st.markdown("""
<style>
    .result-card {
        background-color: #f0f2f6;
        border-radius: 10px;
        padding: 20px;
        text-align: center;
        border: 1px solid #d1d5db;
        margin-bottom: 20px;
    }
    .result-value {
        font-size: 48px;
        font-weight: bold;
        color: #007bff;
    }
    .result-label {
        font-size: 18px;
        color: #333;
        font-weight: 500;
    }
</style>
""", unsafe_allow_html=True)

# --- 3. FUNGSI LOGIKA FUZZY (MEMBERSHIP FUNCTIONS) ---

def trapmf(x, p):
    """Fungsi Trapesium"""
    return np.maximum(0, np.minimum(np.minimum((x - p[0]) / (p[1] - p[0]), 1), (p[3] - x) / (p[3] - p[2])))

def trimf(x, p):
    """Fungsi Segitiga"""
    return np.maximum(0, np.minimum((x - p[0]) / (p[1] - p[0]), (p[2] - x) / (p[2] - p[1])))

# --- 4. DEFINISI VARIABEL (FUZZIFIKASI) ---

def fuzzify_permintaan(x):
    u_kecil = trapmf(x, [778, 975, 1030, 1310])
    u_sedang = trimf(x, [1030, 1310, 1589])
    u_besar = trapmf(x, [1310, 1589, 1695, 1796])
    return u_kecil, u_sedang, u_besar

def fuzzify_persediaan(x):
    u_sedikit = trapmf(x, [492, 588, 607, 750])
    u_sedang = trimf(x, [607, 750, 894])
    u_banyak = trapmf(x, [750, 894, 912, 1008])
    return u_sedikit, u_sedang, u_banyak

# [PERBAIKAN 1] Mengembalikan Fungsi Formula Detail
def get_formula_latex(x, p, label):
    """
    Menghasilkan string LaTeX detail: Rumus -> Substitusi -> Hasil
    """
    # Cek Trapesium (4 parameter)
    if len(p) == 4:
        a, b, c, d = p
        if x <= a or x >= d:
            return f"\\mu_{{{label}}}({x}) = 0 \\quad \\text{{(Di luar range)}}"
        elif b <= x <= c:
            return f"\\mu_{{{label}}}({x}) = 1 \\quad \\text{{(Di area puncak)}}"
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
            return f"\\mu_{{{label}}}({x}) = 0 \\quad \\text{{(Di luar range)}}"
        elif x == b:
            return f"\\mu_{{{label}}}({x}) = 1 \\quad \\text{{(Tepat di puncak)}}"
        elif a < x < b:
            val = (x - a) / (b - a)
            return f"\\mu_{{{label}}}({x}) = \\frac{{x - {a}}}{{{b} - {a}}} = \\frac{{{x - a}}}{{{b - a}}} = {val:.4f}"
        elif b < x < c:
            val = (c - x) / (c - b)
            return f"\\mu_{{{label}}}({x}) = \\frac{{{c} - x}}{{{c} - {b}}} = \\frac{{{c - x}}}{{{c - b}}} = {val:.4f}"
            
    return "Error parsing formula"

# Konstanta Output Sugeno
Z_SEDIKIT = 1996
Z_SEDANG = 2275
Z_BANYAK = 2579

# --- 5. LOGIKA UTAMA (INFERENSI) ---
def calculate_fuzzy_sugeno(in_minta, in_sedia):
    # 1. Fuzzifikasi
    pm_kecil, pm_sedang, pm_besar = fuzzify_permintaan(in_minta)
    ps_sedikit, ps_sedang, ps_banyak = fuzzify_persediaan(in_sedia)

    # 2. Inferensi (Rule Evaluation - Operator MIN)
    rules = []
    
    # Rule 1-3 (Minta KECIL)
    rules.append({"Rule": 1, "Alpha": min(pm_kecil, ps_sedikit), "Z": Z_SEDIKIT, "Ket": "Kecil & Sedikit -> Sedikit"})
    rules.append({"Rule": 2, "Alpha": min(pm_kecil, ps_sedang), "Z": Z_SEDIKIT, "Ket": "Kecil & Sedang -> Sedikit"})
    rules.append({"Rule": 3, "Alpha": min(pm_kecil, ps_banyak), "Z": Z_SEDIKIT, "Ket": "Kecil & Banyak -> Sedikit"})
    
    # Rule 4-6 (Minta SEDANG)
    rules.append({"Rule": 4, "Alpha": min(pm_sedang, ps_sedikit), "Z": Z_SEDIKIT, "Ket": "Sedang & Sedikit -> Sedikit"})
    rules.append({"Rule": 5, "Alpha": min(pm_sedang, ps_sedang), "Z": Z_SEDANG, "Ket": "Sedang & Sedang -> Sedang"})
    rules.append({"Rule": 6, "Alpha": min(pm_sedang, ps_banyak), "Z": Z_SEDANG, "Ket": "Sedang & Banyak -> Sedang"})
    
    # Rule 7-9 (Minta BESAR)
    rules.append({"Rule": 7, "Alpha": min(pm_besar, ps_sedikit), "Z": Z_SEDIKIT, "Ket": "Besar & Sedikit -> Sedikit"})
    rules.append({"Rule": 8, "Alpha": min(pm_besar, ps_sedang), "Z": Z_SEDANG, "Ket": "Besar & Sedang -> Sedang"})
    rules.append({"Rule": 9, "Alpha": min(pm_besar, ps_banyak), "Z": Z_BANYAK, "Ket": "Besar & Banyak -> Banyak"})

    # 3. Defuzzifikasi (Weighted Average)
    numerator = sum(r["Alpha"] * r["Z"] for r in rules)
    denominator = sum(r["Alpha"] for r in rules)
    
    # Menghindari pembagian nol
    result = numerator / denominator if denominator != 0 else 0
    return result, rules

# --- 6. FUNGSI GRAFIK ---
def plot_graph(x_val, input_type):
    fig, ax = plt.subplots(figsize=(8, 3))
    if input_type == "minta":
        x = np.linspace(700, 1800, 500)
        ax.plot(x, trapmf(x, [778, 975, 1030, 1310]), label='Kecil', color='green')
        ax.plot(x, trimf(x, [1030, 1310, 1589]), label='Sedang', color='orange')
        ax.plot(x, trapmf(x, [1310, 1589, 1695, 1796]), label='Besar', color='red')
        title = "Membership Function: Permintaan"
    else:
        x = np.linspace(400, 1100, 500)
        ax.plot(x, trapmf(x, [492, 588, 607, 750]), label='Sedikit', color='green')
        ax.plot(x, trimf(x, [607, 750, 894]), label='Sedang', color='orange')
        ax.plot(x, trapmf(x, [750, 894, 912, 1008]), label='Banyak', color='red')
        title = "Membership Function: Persediaan"

    ax.axvline(x=x_val, color='blue', linestyle='--', linewidth=2, label='Input Anda')
    ax.set_title(title); ax.legend(); ax.grid(True, alpha=0.3)
    ax.spines['top'].set_visible(False); ax.spines['right'].set_visible(False)
    return fig

# --- 7. UI UTAMA ---

# SIDEBAR
with st.sidebar:
    st.header("📚 Knowledge Base")
    st.info("Sumber: Jurnal JPILKOM Hal. 72, Tabel 4")
    st.markdown("""
    **Aturan (Rules) Sistem:**
    1. IF **Kecil** & **Sedikit** THEN **Sedikit**
    2. IF **Kecil** & **Sedang** THEN **Sedikit**
    3. IF **Kecil** & **Banyak** THEN **Sedikit**
    4. IF **Sedang** & **Sedikit** THEN **Sedikit**
    5. IF **Sedang** & **Sedang** THEN **Sedang**
    6. IF **Sedang** & **Banyak** THEN **Sedang**
    7. IF **Besar** & **Sedikit** THEN **Sedikit**
    8. IF **Besar** & **Sedang** THEN **Sedang**
    9. IF **Besar** & **Banyak** THEN **Banyak**
    """)

# JUDUL UTAMA
st.title("🍞 Prediksi Produksi Roti Ganda")
st.markdown("### Tugas UAS: Sistem Berbasis Pengetahuan")
st.markdown("Implementasi Logika Fuzzy Metode Sugeno (Studi Kasus: PT Roti Ganda Siantar)")
st.divider()

col1, col2 = st.columns(2)

with col1:
    st.subheader("Data Permintaan")
    input_minta = st.number_input(
        "Jumlah Permintaan (Bungkus)", 
        min_value=1030, max_value=1589, value=1030, step=1,
        help="Range Data Tabel 3: 1030 - 1589"
    )

with col2:
    st.subheader("Data Persediaan")
    input_sedia = st.number_input(
        "Jumlah Persediaan (Bungkus)", 
        min_value=607, max_value=894, value=607, step=1,
        help="Range Data Tabel 3: 607 - 894"
    )

# HITUNG
hasil, data_rules = calculate_fuzzy_sugeno(input_minta, input_sedia)

# TAMPILKAN HASIL
st.markdown("---")
st.markdown("### 🏭 Hasil Rekomendasi Produksi")
st.markdown(f"""
<div class="result-card">
    <div class="result-label">Jumlah yang harus diproduksi:</div>
    <div class="result-value">{int(round(hasil))}</div>
    <div class="result-label">Bungkus</div>
</div>
""", unsafe_allow_html=True)

# --- DETAIL STEP-BY-STEP (TABS) ---
with st.expander("🔍 Lihat Detail Perhitungan (Step-by-Step)"):
    tab1, tab2, tab3 = st.tabs(["1. Fuzzifikasi", "2. Inferensi", "3. Defuzzifikasi"])
    
    with tab1:
        st.markdown("### 1. Fuzzifikasi (Input -> Derajat Keanggotaan)")
        st.info("Rumus dipilih otomatis berdasarkan posisi nilai input pada grafik.")
        
        c1, c2 = st.columns(2)
        with c1:
            st.markdown(f"**A. Permintaan: {input_minta}**")
            st.pyplot(plot_graph(input_minta, "minta"))
            # Menampilkan rumus LaTeX yang sudah diperbaiki
            st.latex(get_formula_latex(input_minta, [778, 975, 1030, 1310], "Kecil"))
            st.latex(get_formula_latex(input_minta, [1030, 1310, 1589], "Sedang"))
            st.latex(get_formula_latex(input_minta, [1310, 1589, 1695, 1796], "Besar"))
        with c2:
            st.markdown(f"**B. Persediaan: {input_sedia}**")
            st.pyplot(plot_graph(input_sedia, "sedia"))
            # Menampilkan rumus LaTeX yang sudah diperbaiki
            st.latex(get_formula_latex(input_sedia, [492, 588, 607, 750], "Sedikit"))
            st.latex(get_formula_latex(input_sedia, [607, 750, 894], "Sedang"))
            st.latex(get_formula_latex(input_sedia, [750, 894, 912, 1008], "Banyak"))

    with tab2:
        st.markdown("### 2. Inferensi (Evaluasi Aturan)")
        st.write("Menggunakan operator **MIN** untuk mendapatkan nilai Alpha.")
        
        df_rules = pd.DataFrame(data_rules)
        
        # [PERBAIKAN: Highlight Sebaris Penuh]
        # Fungsi ini menerima satu baris data (Series)
        # Jika nilai 'Alpha' di baris tersebut > 0, warnai seluruh kolom hijau.
        def highlight_active_rows(row):
            if row["Alpha"] > 0:
                return ['background-color: #d1e7dd'] * len(row)
            else:
                return [''] * len(row)

        # Gunakan axis=1 agar fungsi diaplikasikan per baris
        st.dataframe(df_rules.style.apply(highlight_active_rows, axis=1), use_container_width=True)
    
    with tab3:
        st.markdown("### 3. Defuzzifikasi (Weighted Average)")
        st.write("Menghitung rata-rata tertimbang. Hanya rule dengan nilai **α > 0** yang dimasukkan ke dalam perhitungan.")
        active_rules = [r for r in data_rules if r["Alpha"] > 0]
        
        if active_rules:
            num_str = " + ".join([f"({r['Alpha']:.3f} \\times {r['Z']})" for r in active_rules])
            den_str = " + ".join([f"{r['Alpha']:.3f}" for r in active_rules])
            numerator = sum(r["Alpha"] * r["Z"] for r in active_rules)
            denominator = sum(r["Alpha"] for r in active_rules)
            
            st.markdown("**Detail Substitusi Nilai:**")
            st.latex(f"Z = \\frac{{{num_str}}}{{{den_str}}}")
            st.latex(f"Z = \\frac{{{numerator:.4f}}}{{{denominator:.4f}}} = \\mathbf{{{hasil:.4f}}}")
        else:
            st.error("Nilai input di luar jangkauan fuzzy.")