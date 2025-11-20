import streamlit as st
import numpy as np
from sugeno_engine import get_sugeno_score, RULE_COMBOS, Z_RULE, TERM
from fuzzy_variables import fuzzify_inputs

st.set_page_config(page_title="Fuzzy Sugeno Ranking", page_icon="📊", layout="centered")

st.title("📊 Fuzzy Sugeno Ranking System")
st.write("Masukkan nilai untuk setiap parameter, lalu klik **Hitung Skor**.")
st.write("Klik tombol **Lihat Cara Sistem Menghitung** untuk memahami proses lengkapnya.")

# ----------------------------
# Helper: convert text input to float or None
# ----------------------------
def parse_float(x):
    try:
        v = float(x)
        if 0 <= v <= 100:
            return v
        return None
    except:
        return None


# ----------------------------
# Input form (tanpa nilai default)
# ----------------------------
with st.form("input_form"):
    tlr_txt = st.text_input("TLR (Teaching, Learning & Resources)", placeholder="0 – 100")
    rpp_txt = st.text_input("RPP (Research & Professional Practice)", placeholder="0 – 100")
    go_txt  = st.text_input("GO (Graduation Outcomes)", placeholder="0 – 100")
    oi_txt  = st.text_input("OI (Outreach & Inclusivity)", placeholder="0 – 100")
    pr_txt  = st.text_input("PR (Perception)", placeholder="0 – 100")

    col1, col2 = st.columns(2)
    submit = col1.form_submit_button("Hitung Skor")
    debug_btn = col2.form_submit_button("Lihat Cara Sistem Menghitung")


# ----------------------------
# Parse nilai input
# ----------------------------
inputs = {
    "tlr": parse_float(tlr_txt),
    "rpp": parse_float(rpp_txt),
    "go":  parse_float(go_txt),
    "oi":  parse_float(oi_txt),
    "pr":  parse_float(pr_txt),
}

valid = all(v is not None for v in inputs.values())


# ====================================================
# 1. Tombol Hitung Skor
# ====================================================
if submit:
    if not valid:
        st.error("Semua input harus berupa angka dalam rentang 0–100.")
    else:
        score = get_sugeno_score(
            inputs["tlr"], inputs["rpp"], inputs["go"],
            inputs["oi"], inputs["pr"]
        )
        st.success(f"Skor Sugeno: {score:.2f}")


# ====================================================
# 2. Tombol Debug – tampilkan proses perhitungan lengkap
# ====================================================
if debug_btn:
    if not valid:
        st.error("Semua input harus berupa angka valid untuk menampilkan proses.")
    else:
        tlr = inputs["tlr"]
        rpp = inputs["rpp"]
        go  = inputs["go"]
        oi  = inputs["oi"]
        pr  = inputs["pr"]

        st.subheader("📌 Langkah 1 – Fuzzification (μ derajat keanggotaan)")

        fuzz = fuzzify_inputs(tlr, rpp, go, oi, pr)
        st.write(fuzz)

        st.subheader("📌 Langkah 2 – Hitung Firing Strength (wᵢ = MIN dari μ)")

        numerator = 0.0
        denominator = 0.0

        debug_rows = []

        for i, combo in enumerate(RULE_COMBOS):
            mus = [
                fuzz["tlr"][TERM[combo[0]]],
                fuzz["rpp"][TERM[combo[1]]],
                fuzz["go"][TERM[combo[2]]],
                fuzz["oi"][TERM[combo[3]]],
                fuzz["pr"][TERM[combo[4]]],
            ]
            w = min(mus)

            if w > 0:
                numerator += w * Z_RULE[i]
                denominator += w
                debug_rows.append({
                    "Rule index": i,
                    "Combo": combo,
                    "μ values": mus,
                    "w (min μ)": w,
                    "Z_RULE[i]": float(Z_RULE[i]),
                    "w * Z": w * float(Z_RULE[i])
                })

        st.write("### 🔍 Rule yang aktif (w > 0)")
        st.dataframe(debug_rows)

        st.subheader("📌 Langkah 3 – Defuzzifikasi Sugeno (Weighted Average)")

        if denominator == 0:
            st.write("Denominator 0 – fallback ke rata-rata input.")
            score = (tlr + rpp + go + oi + pr) / 5
        else:
            score = numerator / denominator

        st.write(f"**Numerator:** {numerator}")
        st.write(f"**Denominator:** {denominator}")
        st.write(f"### 🎯 Skor Akhir: **{score:.4f}**")
