# fuzzy_variables.py
# Orang1 (Rian) akan mengisi file ini dengan definisi fuzzy variables dan membership functions

"""
fuzzy_variables.py

Definisi variabel fuzzy (input) dan membership functions
untuk sistem Sugeno UAS Sistem Berbasis Pengetahuan.

Tugas Orang 1:
- Mendefinisikan 5 input: TLR, RPP, GO, OI, PR.
- Membuat triangular membership functions: Low, Medium, High.
- Menyusun struktur FIS (tanpa rule).

Catatan:
- Range default semua input: 0–100 (bisa diubah lewat konfigurasi).
- Menggunakan scikit-fuzzy (skfuzzy) untuk universes & membership.
- Disediakan fungsi helper untuk:
  - Mengambil struktur FIS,
  - Melihat definisi variabel,
  - Melakukan fuzzifikasi (menghitung derajat keanggotaan).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Any

import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl


# ============================================================
# 1. Konfigurasi global untuk Fuzzy Input
# ============================================================

# Asumsi nilai tiap indikator dalam skala 0–100
UNIVERSE_MIN: float = 0.0
UNIVERSE_MAX: float = 100.0
UNIVERSE_STEP: float = 0.5  # makin kecil = resolusi lebih halus

# Universe umum untuk semua input
INPUT_UNIVERSE: np.ndarray = np.arange(
    UNIVERSE_MIN, UNIVERSE_MAX + UNIVERSE_STEP, UNIVERSE_STEP
)


@dataclass(frozen=True)
class MembershipConfig:
    """
    Konfigurasi bentuk membership function triangular
    untuk Low, Medium, High pada satu variabel fuzzy.

    Setiap field berisi 3 titik (a, b, c) untuk fungsi trimf.
    """

    low: tuple[float, float, float]
    medium: tuple[float, float, float]
    high: tuple[float, float, float]


# Default: pembagian sederhana 0–100 → Low, Medium, High
DEFAULT_MEMBERSHIP_CONFIG = MembershipConfig(
    low=(UNIVERSE_MIN, UNIVERSE_MIN, 50.0),
    medium=(25.0, 50.0, 75.0),
    high=(50.0, UNIVERSE_MAX, UNIVERSE_MAX),
)


# Nama variabel input yang digunakan di seluruh sistem
INPUT_NAMES = ["tlr", "rpp", "go", "oi", "pr"]


# ============================================================
# 2. Pembuatan variabel fuzzy (Antecedent) + membership
# ============================================================

def _create_input_variable(
    name: str,
    universe: np.ndarray = INPUT_UNIVERSE,
    config: MembershipConfig = DEFAULT_MEMBERSHIP_CONFIG,
) -> ctrl.Antecedent:
    """
    Membuat satu variabel input fuzzy (Antecedent) lengkap dengan
    membership function Low, Medium, High (triangular).

    Parameters
    ----------
    name : str
        Nama internal variabel, misalnya: 'tlr', 'rpp', 'go', 'oi', 'pr'.
    universe : np.ndarray
        Range nilai untuk variabel.
    config : MembershipConfig
        Konfigurasi titik triangular MF (Low, Medium, High).

    Returns
    -------
    antecedent : ctrl.Antecedent
        Objek Antecedent scikit-fuzzy yang siap dipakai di FIS.
    """
    var = ctrl.Antecedent(universe, name)

    # Definisi membership function menggunakan trimf
    var["low"] = fuzz.trimf(universe, config.low)
    var["medium"] = fuzz.trimf(universe, config.medium)
    var["high"] = fuzz.trimf(universe, config.high)

    return var


# Buat semua input sekali di sini (singleton pattern sederhana)
TLR: ctrl.Antecedent = _create_input_variable("tlr")
RPP: ctrl.Antecedent = _create_input_variable("rpp")
GO: ctrl.Antecedent = _create_input_variable("go")
OI: ctrl.Antecedent = _create_input_variable("oi")
PR: ctrl.Antecedent = _create_input_variable("pr")

# Kumpulan semua input dalam dict untuk akses mudah
INPUT_VARIABLES: Dict[str, ctrl.Antecedent] = {
    "tlr": TLR,
    "rpp": RPP,
    "go": GO,
    "oi": OI,
    "pr": PR,
}


# ============================================================
# 3. Struktur FIS (tanpa rule)
#    - Disiapkan supaya Orang 2 bisa menambahkan rule Mamdani
#      jika dibutuhkan, walaupun inference Sugeno dilakukan manual.
# ============================================================

@dataclass
class FISStructure:
    """
    Representasi sederhana struktur FIS untuk input saja.

    Attributes
    ----------
    universe : np.ndarray
        Universe yang dipakai oleh semua input.
    inputs : Dict[str, ctrl.Antecedent]
        Dictionary nama → variabel fuzzy (Antecedent).
    control_system : ctrl.ControlSystem
        ControlSystem scikit-fuzzy (tanpa rule).
        Bisa di-extend oleh orang lain jika mau.
    """
    universe: np.ndarray
    inputs: Dict[str, ctrl.Antecedent]
    control_system: ctrl.ControlSystem


def build_empty_control_system(
    inputs: Dict[str, ctrl.Antecedent] | None = None,
) -> ctrl.ControlSystem:
    """
    Membuat ControlSystem kosong (tanpa rule).

    Ini hanya untuk melengkapi struktur FIS berdasarkan scikit-fuzzy,
    sehingga jika Orang 2 ingin menggunakan rule Mamdani, sistemnya
    sudah siap. Untuk inference Sugeno, biasanya engine akan dibuat
    manual di file `sugeno_engine.py`.
    """
    if inputs is None:
        inputs = INPUT_VARIABLES

    # Saat ini tidak ada rule; rule akan didefinisikan di modul lain jika perlu
    control_system = ctrl.ControlSystem(rules=[])

    # scikit-fuzzy akan otomatis mengetahui variabel dari rules.
    # Karena belum ada rule, kita tidak perlu men-attach variabel manual di sini.
    return control_system


def get_fis_structure() -> FISStructure:
    """
    Mengembalikan struktur FIS yang berisi:
    - Universe input
    - Semua variabel input fuzzy
    - ControlSystem (tanpa rule)

    Fungsi ini bisa dipanggil oleh modul lain untuk mendapatkan
    gambaran lengkap FIS berbasis scikit-fuzzy.
    """
    cs = build_empty_control_system(INPUT_VARIABLES)
    return FISStructure(
        universe=INPUT_UNIVERSE,
        inputs=INPUT_VARIABLES,
        control_system=cs,
    )


# ============================================================
# 4. Helper fuzzification untuk dipakai Sugeno Engine
# ============================================================

def fuzzify_single_input(
    variable: ctrl.Antecedent,
    value: float,
) -> Dict[str, float]:
    """
    Menghitung derajat keanggotaan (μ) untuk satu variabel fuzzy
    pada semua term (low, medium, high) terhadap nilai crisp.

    Parameters
    ----------
    variable : ctrl.Antecedent
        Variabel input fuzzy (misalnya TLR, RPP, dsb).
    value : float
        Nilai crisp yang ingin difuzzifikasi.

    Returns
    -------
    degrees : Dict[str, float]
        Mapping term_name → degree, misalnya:
        {'low': 0.2, 'medium': 0.8, 'high': 0.0}
    """
    universe = variable.universe
    degrees: Dict[str, float] = {}

    for term_name, term_obj in variable.terms.items():
        # term_obj.mf berisi nilai fungsi keanggotaan di seluruh universe
        mu = fuzz.interp_membership(universe, term_obj.mf, value)
        degrees[term_name] = float(mu)

    return degrees


def fuzzify_inputs(
    tlr: float,
    rpp: float,
    go: float,
    oi: float,
    pr: float,
) -> Dict[str, Dict[str, float]]:
    """
    Melakukan fuzzifikasi untuk kelima input sekaligus.

    Parameters
    ----------
    tlr, rpp, go, oi, pr : float
        Nilai crisp masing-masing indikator (0–100).

    Returns
    -------
    result : Dict[str, Dict[str, float]]
        Contoh output:
        {
          'tlr': {'low': μ1, 'medium': μ2, 'high': μ3},
          'rpp': {...},
          'go':  {...},
          'oi':  {...},
          'pr':  {...}
        }

    Fungsi ini sangat berguna untuk Sugeno Inference Engine:
    - Orang 3 bisa memakai hasil ini untuk menghitung firing strength
      tiap rule berdasarkan kombinasi level (1: low, 2: medium, 3: high).
    """
    return {
        "tlr": fuzzify_single_input(TLR, tlr),
        "rpp": fuzzify_single_input(RPP, rpp),
        "go": fuzzify_single_input(GO, go),
        "oi": fuzzify_single_input(OI, oi),
        "pr": fuzzify_single_input(PR, pr),
    }
