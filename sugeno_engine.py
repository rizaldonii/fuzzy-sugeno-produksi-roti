# sugeno_engine.py
"""
Final Sugeno Engine
Uses:
 • 243 rules (all combinations of 1..3)
 • MIN operator for firing strength
 • Weighted average defuzzification
 • Z_RULE loaded from precomputed bounded file (0–100)
"""

import numpy as np
from itertools import product
from fuzzy_variables import fuzzify_inputs
import os

# 1. Generate 243 rule antecedent combinations
RULE_COMBOS = list(product([1, 2, 3], repeat=5))

# 2. Mapping 1/2/3 → fuzzy term names
TERM = {1:"low", 2:"medium", 3:"high"}

# 3. Load the precomputed bounded rule consequents (0–100)
Z_RULE_PATH = os.path.join(os.path.dirname(__file__), "z_rule_bounded_final.npy")

if not os.path.exists(Z_RULE_PATH):
    raise FileNotFoundError(
        "\n[z_rule_bounded.npy] tidak ditemukan.\n"
        "Pastikan file tersebut berada di folder yang sama dengan sugeno_engine.py.\n"
    )

Z_RULE = np.load(Z_RULE_PATH)


# -------------------------------------------------------
# 4. Prediksi Sugeno (dipanggil dari web/app)
# -------------------------------------------------------
def get_sugeno_score(tlr, rpp, go, oi, pr):
    fuzz = fuzzify_inputs(tlr, rpp, go, oi, pr)
    num = 0.0
    den = 0.0

    for i, combo in enumerate(RULE_COMBOS):
        μ = [
            fuzz["tlr"][TERM[combo[0]]],
            fuzz["rpp"][TERM[combo[1]]],
            fuzz["go"][TERM[combo[2]]],
            fuzz["oi"][TERM[combo[3]]],
            fuzz["pr"][TERM[combo[4]]],
        ]
        w = min(μ)  # MIN operator

        if w > 0:
            num += w * Z_RULE[i]
            den += w

    if den == 0:
        return float((tlr + rpp + go + oi + pr) / 5.0)

    return float(num / den)


# -------------------------------------------------------
# 5. Opsional — verifikasi training set
# -------------------------------------------------------
TRAINING = np.array([
    [84.57,83.54,87.13,66.08,94.14,97.2],
    [83.16,89.24,78.56,50.69,86.92,94.4],
    [78.3,82.98,79.13,58.58,86.14,86.2],
    [76.95,84.37,82.32,50.69,86.92,88.7],
    [67.35,76.65,86.17,60.63,78.11,82.7],
    [71.96,69.61,69.96,50.39,75.68,62.6],
    [76.75,41.85,99.87,75.87,55.27,89.6],
    [67.32,65.08,87.14,61.64,43.66,63.2],
    [76.8,56.58,73.87,60.63,46.34,63.5],
    [69.72,46.48,96.37,57.02,47.28,66.2],
    [74.81,43.77,83.65,58.77,36.71,67.3],
    [62.26,47.1,91.54,60.14,37.39,53.6],
    [54.39,54.89,90.28,44.95,51.83,50.0],
    [56.39,54.09,78.07,53.16,62.72,52.7],
    [73.02,43.77,70.28,70.23,31.01,61.7],
    [77.9,38.32,69.71,66.78,30.21,60.7],
    [69.25,44.42,86.04,54.33,16.55,52.9],
    [76.69,35.38,85.66,57.57,18.46,55.7],
    [73.75,32.04,88.53,71.97,14.26,59.2],
    [47.86,53.8,87.18,55.41,41.11,50.0],
])

def verify_on_training():
    preds = []
    for row in TRAINING:
        preds.append(get_sugeno_score(*row[:5]))
    return np.array(preds)
