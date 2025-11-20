# fuzzy_variables.py
"""
Membership functions (Table 2):
 Low  = (-40, 0, 40)
 Med  = (10, 50, 90)
 High = (60, 100, 140)
"""

from typing import Dict, Tuple
import numpy as np

LOW_TRI = (-40.0, 0.0, 40.0)
MED_TRI = (10.0, 50.0, 90.0)
HIGH_TRI = (60.0, 100.0, 140.0)

def trimf_scalar(x: float, abc: Tuple[float, float, float]) -> float:
    a, b, c = abc
    if x <= a or x >= c:
        return 0.0
    if x == b:
        return 1.0
    if a < x < b:
        return (x - a) / (b - a)
    return (c - x) / (c - b)

def fuzzify_value(value: float) -> Dict[str, float]:
    return {
        "low": trimf_scalar(value, LOW_TRI),
        "medium": trimf_scalar(value, MED_TRI),
        "high": trimf_scalar(value, HIGH_TRI),
    }

def fuzzify_inputs(tlr, rpp, go, oi, pr):
    return {
        "tlr": fuzzify_value(tlr),
        "rpp": fuzzify_value(rpp),
        "go":  fuzzify_value(go),
        "oi":  fuzzify_value(oi),
        "pr":  fuzzify_value(pr),
    }
