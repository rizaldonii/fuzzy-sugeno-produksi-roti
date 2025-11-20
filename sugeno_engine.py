# sugeno_engine.py
"""
Sugeno engine (manual) - menghitung skor dengan metode Weighted Average.
Menggunakan:
- fuzzify_inputs(...) dari fuzzy_variables
- rules list dari fuzzy_rules.load_all_rules()

Setiap rule: consequent adalah konstanta sesuai LEVEL_OUTPUT_VALUE mapping.
Firing strength rule = min(μ_i untuk tiap antecedent sesuai rule).
Output = sum(w_i * z_i) / sum(w_i)
"""

from typing import Dict
from fuzzy_variables import fuzzify_inputs
from fuzzy_rules import load_all_rules

# Mapping level -> crisp output value untuk Sugeno
# Pilihan default: 1 -> 0, 2 -> 50, 3 -> 100  (editable)
LEVEL_OUTPUT_VALUE = {
    1: 0.0,
    2: 50.0,
    3: 100.0,
}

def get_sugeno_score(tlr_val: float, rpp_val: float, go_val: float, oi_val: float, pr_val: float) -> float:
    """
    Hitung skor Sugeno untuk satu baris input.
    """
    # 1) fuzzify inputs -> dict nama -> {term: μ}
    fuzz = fuzzify_inputs(tlr_val, rpp_val, go_val, oi_val, pr_val)

    # 2) load rules (list of dict)
    rules = load_all_rules()
    if not rules:
        raise RuntimeError("No rules loaded. Pastikan fuzzy_rules.load_all_rules() bekerja.")

    numerator = 0.0
    denominator = 0.0

    # helper mapping level int -> term name lowercase
    level_to_term = {1: "low", 2: "medium", 3: "high"}

    for r in rules:
        # untuk tiap rule ambil derajat keanggotaan yang sesuai
        mu_tlr = fuzz["tlr"].get(level_to_term[r["tlr"]], 0.0)
        mu_rpp = fuzz["rpp"].get(level_to_term[r["rpp"]], 0.0)
        mu_go  = fuzz["go"].get(level_to_term[r["go"]], 0.0)
        mu_oi  = fuzz["oi"].get(level_to_term[r["oi"]], 0.0)
        mu_pr  = fuzz["pr"].get(level_to_term[r["pr"]], 0.0)

        # firing strength = MIN dari semua antecedent μ
        firing_strength = min(mu_tlr, mu_rpp, mu_go, mu_oi, mu_pr)

        if firing_strength <= 0.0:
            continue  # rule tidak aktif, skip

        # consequent crisp value (z)
        z = LEVEL_OUTPUT_VALUE.get(r["out"], 0.0)

        numerator += firing_strength * z
        denominator += firing_strength

    if denominator == 0.0:
        # tidak ada rule aktif: fallback (mis: rata-rata input)
        return (tlr_val + rpp_val + go_val + oi_val + pr_val) / 5.0

    score = numerator / denominator
    return float(score)


# -- Optional: quick test when run directly
if __name__ == "__main__":
    # contoh: IITM dari tabel paper
    s = get_sugeno_score(84.57, 83.54, 87.13, 66.08, 94.14)
    print("Sugeno score (IITM sample):", s)
    s2 = get_sugeno_score(10,10,10,10,10)
    print("Low sample:", s2)
