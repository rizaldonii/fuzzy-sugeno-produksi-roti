# web_app.py
import streamlit as st

# coba import get_sugeno_score; jika belum tersedia gunakan dummy
try:
    from sugeno_engine import get_sugeno_score
except Exception:
    def get_sugeno_score(tlr, rpp, go, oi, pr):
        # dummy placeholder: rata-rata, nanti diganti dengan import asli
        return (tlr + rpp + go + oi + pr) / 5

st.set_page_config(page_title="Fuzzy Sugeno Ranking", page_icon="📊", layout="centered")

st.title("📊 Fuzzy Sugeno Ranking System")
st.write("Masukkan nilai untuk setiap parameter lalu klik **Hitung Skor**.")

with st.form("input_form"):
    tlr = st.number_input("TLR (Teaching, Learning & Resources)", min_value=0.0, max_value=200.0, value=70.0, step=0.1)
    rpp = st.number_input("RPP (Research & Professional Practice)", min_value=0.0, max_value=200.0, value=70.0, step=0.1)
    go  = st.number_input("GO (Graduation Outcomes)", min_value=0.0, max_value=200.0, value=70.0, step=0.1)
    oi  = st.number_input("OI (Outreach & Inclusivity)", min_value=0.0, max_value=200.0, value=50.0, step=0.1)
    pr  = st.number_input("PR (Perception)", min_value=0.0, max_value=200.0, value=80.0, step=0.1)
    submit = st.form_submit_button("Hitung Skor")

if submit:
    score = get_sugeno_score(tlr, rpp, go, oi, pr)
    st.success(f"Skor Sugeno: {score:.2f}")
