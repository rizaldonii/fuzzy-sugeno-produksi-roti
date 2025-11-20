# fuzzy_rules.py
"""
Rule generator untuk Sugeno (manual).
Menghasilkan 243 kombinasi (1..3 untuk tiap input) dan menentukan
level output (1: low, 2: medium, 3: high) berdasarkan bobot.
Fungsi utama: load_all_rules() -> list of dict
Format dict: {"tlr":1,"rpp":2,"go":3,"oi":1,"pr":2,"out":2}
"""

import itertools

# Nilai level
VAL_LOW = 1
VAL_MED = 2
VAL_HIGH = 3

# Bobot sesuai paper: TLR(3), RPP(3), GO(2), OI(1), PR(1)
WEIGHTS = [3, 3, 2, 1, 1]

def _calculate_output_level(combo):
    """
    Tentukan level output berdasarkan bobot kombinasi.
    Ini adalah heuristik yang sama dengan implementasi awal; bisa disesuaikan.
    """
    score = sum(i * w for i, w in zip(combo, WEIGHTS))
    # ambang sederhana (sesuaikan jika tim ingin replicasi persis)
    if score <= 12:
        return VAL_LOW
    elif score >= 21:
        return VAL_HIGH
    else:
        return VAL_MED

def _generate_rules_data():
    items = itertools.product([VAL_LOW, VAL_MED, VAL_HIGH], repeat=5)
    rules = []
    for combo in items:
        out = _calculate_output_level(combo)
        rules.append({
            "tlr": combo[0],
            "rpp": combo[1],
            "go":  combo[2],
            "oi":  combo[3],
            "pr":  combo[4],
            "out": out
        })
    return rules

def load_all_rules():
    """Return list of rule dicts (length 243)."""
    return _generate_rules_data()
