"""
Variabel fuzzy + helper fuzzification.
Nama term: 'low', 'medium', 'high' (lowercase!)
"""
from dataclasses import dataclass
from typing import Dict
import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl

# Universe (0..100)
UNIVERSE_MIN = 0.0
UNIVERSE_MAX = 100.0
UNIVERSE_STEP = 0.5
INPUT_UNIVERSE = np.arange(UNIVERSE_MIN, UNIVERSE_MAX + UNIVERSE_STEP, UNIVERSE_STEP)

@dataclass(frozen=True)
class MembershipConfig:
    low: tuple
    medium: tuple
    high: tuple

# Konfigurasi triangular (bisa disesuaikan jika ingin match paper lebih ketat)
DEFAULT_MEMBERSHIP_CONFIG = MembershipConfig(
    low=(UNIVERSE_MIN, UNIVERSE_MIN, 50.0),
    medium=(25.0, 50.0, 75.0),
    high=(50.0, UNIVERSE_MAX, UNIVERSE_MAX),
)

# Helper untuk membuat Antecedent dengan term 'low','medium','high'
def _create_input_variable(name: str, universe=INPUT_UNIVERSE, config=DEFAULT_MEMBERSHIP_CONFIG):
    var = ctrl.Antecedent(universe, name)
    var['low'] = fuzz.trimf(universe, config.low)
    var['medium'] = fuzz.trimf(universe, config.medium)
    var['high'] = fuzz.trimf(universe, config.high)
    return var

# Buat variabel input
TLR = _create_input_variable("tlr")
RPP = _create_input_variable("rpp")
GO  = _create_input_variable("go")
OI  = _create_input_variable("oi")
PR  = _create_input_variable("pr")

# Kumpulan untuk akses
INPUT_VARIABLES = {
    "tlr": TLR,
    "rpp": RPP,
    "go": GO,
    "oi": OI,
    "pr": PR,
}

# Untuk kompatibilitas dengan modul rule loader sebelumnya:
antecedents = (TLR, RPP, GO, OI, PR)

# --- Fuzzification helpers (dipakai engine Sugeno) ---
def fuzzify_single_input(variable: ctrl.Antecedent, value: float):
    """Return dict term -> μ (float) untuk satu variabel."""
    universe = variable.universe
    degrees = {}
    # setiap term di variable.terms (dict)
    for term_name, term_obj in variable.terms.items():
        mu = fuzz.interp_membership(universe, term_obj.mf, value)
        degrees[term_name] = float(mu)
    return degrees

def fuzzify_inputs(tlr: float, rpp: float, go: float, oi: float, pr: float):
    """Kembalikan dict nama_input -> {term: degree}"""
    return {
        "tlr": fuzzify_single_input(TLR, tlr),
        "rpp": fuzzify_single_input(RPP, rpp),
        "go":  fuzzify_single_input(GO, go),
        "oi":  fuzzify_single_input(OI, oi),
        "pr":  fuzzify_single_input(PR, pr),
    }