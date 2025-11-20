import streamlit as st
import pandas as pd
from sugeno_engine import get_sugeno_score, RULE_COMBOS, TERM, Z_RULE
from fuzzy_variables import fuzzify_inputs

st.set_page_config(
    page_title="Fuzzy Sugeno Ranking",
    page_icon="📊",
    layout="centered",
    initial_sidebar_state="collapsed"
)


st.title("📊 Fuzzy Sugeno Ranking System")
st.markdown("### Masukkan nilai parameter lalu klik tombol untuk melihat hasil")
st.write("*Gunakan titik (.) untuk angka desimal, misalnya: 85.5*")


with st.form("input_form"):
    st.markdown("#### Parameter Input")
    
    col_input1, col_input2 = st.columns(2)
    
    with col_input1:
        tlr = st.number_input("TLR (Teacher-to-Learner Ratio)", 
                             min_value=0.0, max_value=100.0, value=0.0, step=0.1,
                             format="%.2f", help="Masukkan nilai dengan titik desimal, contoh: 85.5")
        go  = st.number_input("GO (Government Ownership)",  
                             min_value=0.0, max_value=100.0, value=0.0, step=0.1,
                             format="%.2f", help="Masukkan nilai dengan titik desimal, contoh: 85.5")
        pr  = st.number_input("PR (Publication Rate)",  
                             min_value=0.0, max_value=100.0, value=0.0, step=0.1,
                             format="%.2f", help="Masukkan nilai dengan titik desimal, contoh: 85.5")
    
    with col_input2:
        rpp = st.number_input("RPP (Research Publication Performance)", 
                             min_value=0.0, max_value=100.0, value=0.0, step=0.1,
                             format="%.2f", help="Masukkan nilai dengan titik desimal, contoh: 85.5")
        oi  = st.number_input("OI (Organizational Infrastructure)",  
                             min_value=0.0, max_value=100.0, value=0.0, step=0.1,
                             format="%.2f", help="Masukkan nilai dengan titik desimal, contoh: 85.5")

    st.markdown("---")
    col1, col2 = st.columns(2)
    with col1:
        submit_score = st.form_submit_button("Hitung Skor", use_container_width=True)
    with col2:
        submit_debug = st.form_submit_button("Lihat Cara Kerja Sistem", use_container_width=True)

# ------------------------------------------------------
# MODE 1 — Hanya menampilkan skor akhir
# ------------------------------------------------------
if submit_score:
    try:
        score = get_sugeno_score(tlr, rpp, go, oi, pr)
        st.success(f"**Skor Sugeno: {score:.4f}**")
        
        # Display input values for confirmation
        with st.expander("Nilai Input yang Digunakan"):
            input_df = pd.DataFrame({
                'Parameter': ['TLR', 'RPP', 'GO', 'OI', 'PR'],
                'Nilai': [f"{tlr:.2f}", f"{rpp:.2f}", f"{go:.2f}", f"{oi:.2f}", f"{pr:.2f}"]
            })
            st.dataframe(input_df, use_container_width=True, hide_index=True)
    except Exception as e:
        st.error(f"Error: {e}")

# ------------------------------------------------------
# MODE 2 — Menampilkan proses fuzzy lengkap
# ------------------------------------------------------
if submit_debug:
    try:
        st.markdown("---")
        st.subheader("Proses Lengkap Perhitungan Fuzzy Sugeno")

        # Display input values
        with st.expander("Nilai Input", expanded=True):
            input_df = pd.DataFrame({
                'Parameter': ['TLR', 'RPP', 'GO', 'OI', 'PR'],
                'Nilai': [f"{tlr:.2f}", f"{rpp:.2f}", f"{go:.2f}", f"{oi:.2f}", f"{pr:.2f}"]
            })
            st.dataframe(input_df, use_container_width=True, hide_index=True)

        # -------------------------
        # 1. Fuzzifikasi
        # -------------------------
        fuzz = fuzzify_inputs(tlr, rpp, go, oi, pr)

        st.markdown("### 1. Fuzzifikasi Input")
        st.write("Konversi nilai crisp menjadi derajat keanggotaan fuzzy:")
        fuzz_df = pd.DataFrame(fuzz).T
        st.dataframe(fuzz_df, use_container_width=True)

        # -------------------------
        # 2. Evaluasi Rule
        # -------------------------
        st.markdown("### 2. Perhitungan Setiap Rule")
        st.write("Evaluasi rule dengan metode MIN untuk mendapatkan bobot (w):")
        rows = []

        numerator = 0.0
        denominator = 0.0

        for i, combo in enumerate(RULE_COMBOS):

            μ_vals = [
                fuzz["tlr"][TERM[combo[0]]],
                fuzz["rpp"][TERM[combo[1]]],
                fuzz["go"][TERM[combo[2]]],
                fuzz["oi"][TERM[combo[3]]],
                fuzz["pr"][TERM[combo[4]]],
            ]

            w = min(μ_vals)

            if w > 0:
                z = float(Z_RULE[i])
                contrib = w * z
                numerator += contrib
                denominator += w

                rows.append({
                    "Rule": f"R{i+1}",
                    "Kombinasi": str(combo),
                    "μ Values": [f"{v:.4f}" for v in μ_vals],
                    "w (min μ)": f"{w:.4f}",
                    "Z": f"{z:.4f}",
                    "w × Z": f"{contrib:.4f}"
                })

        df = pd.DataFrame(rows)
        st.dataframe(df, use_container_width=True, hide_index=True)

        # -------------------------
        # 3. Defuzzifikasi
        # -------------------------
        st.markdown("### 3. Defuzzifikasi Sugeno")
        st.write("Hitung skor akhir menggunakan weighted average:")

        col_def1, col_def2 = st.columns(2)
        with col_def1:
            st.metric("Numerator (Σw×Z)", f"{numerator:.4f}")
        with col_def2:
            st.metric("Denominator (Σw)", f"{denominator:.4f}")

        if denominator == 0:
            score = (tlr + rpp + go + oi + pr) / 5
            st.warning(f"Tidak ada rule aktif. Menggunakan rata-rata lima input: {score:.4f}")
        else:
            score = numerator / denominator
            st.info(f"**Formula:** Skor = Numerator / Denominator = {numerator:.4f} / {denominator:.4f}")

        st.success(f"**Skor Akhir: {score:.4f}**")

    except Exception as e:
        st.error(f"Error: {e}")
