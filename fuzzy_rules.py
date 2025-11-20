# fuzzy_rules.py
"""
Generate 243 combinations of fuzzy antecedent levels.
Each combo is a tuple of 5 elements in {1,2,3}.
"""

import itertools

VAL_LOW = 1
VAL_MED = 2
VAL_HIGH = 3

WEIGHTS = [3,3,2,1,1]

def _calculate_output_level(combo):
    s = sum(i * w for i, w in zip(combo, WEIGHTS))
    if s <= 12:
        return VAL_LOW
    elif s >= 21:
        return VAL_HIGH
    else:
        return VAL_MED

def load_all_rules():
    rules = []
    for combo in itertools.product([1,2,3], repeat=5):
        rules.append({
            "tlr": combo[0],
            "rpp": combo[1],
            "go":  combo[2],
            "oi":  combo[3],
            "pr":  combo[4],
            "out": _calculate_output_level(combo)
        })
    return rules
