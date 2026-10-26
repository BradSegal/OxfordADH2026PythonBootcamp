# SPDX-FileCopyrightText: 2026 Bradley Segal
# SPDX-License-Identifier: MIT

"""Clinical reference rules used across the bootcamp.

This module is the single owner of every clinical threshold in the course.
Solutions, checkers and the extension project all import from here, so a
threshold can only ever be wrong in one place.

These are teaching implementations. They are not validated for clinical use.

NEWS2 follows the Royal College of Physicians chart (2017). SpO2 scale 1 is the
default; scale 2 is for patients with a prescribed target range of 88-92%
(for example, hypercapnic respiratory failure).
"""

from __future__ import annotations

LB_PER_KG = 2.20462

# --- Unit conversions -------------------------------------------------------


def lb_to_kg(pounds: float) -> float:
    return pounds / LB_PER_KG


def fahrenheit_to_celsius(fahrenheit: float) -> float:
    return (fahrenheit - 32) * 5 / 9


def weight_based_dose_mg(weight_kg: float, mg_per_kg: float) -> float:
    return weight_kg * mg_per_kg


# --- Body mass index --------------------------------------------------------


def bmi(weight_kg: float, height_m: float) -> float:
    return weight_kg / height_m**2


def bmi_category(value: float) -> str:
    """Adult BMI category (WHO bands)."""
    if value < 18.5:
        return "underweight"
    if value < 25:
        return "healthy"
    if value < 30:
        return "overweight"
    return "obese"


# --- NEWS2 single-parameter scores ------------------------------------------


def score_respiration_rate(breaths_per_min: float) -> int:
    if breaths_per_min <= 8:
        return 3
    if breaths_per_min <= 11:
        return 1
    if breaths_per_min <= 20:
        return 0
    if breaths_per_min <= 24:
        return 2
    return 3


def score_spo2_scale1(spo2: float) -> int:
    if spo2 <= 91:
        return 3
    if spo2 <= 93:
        return 2
    if spo2 <= 95:
        return 1
    return 0


def score_spo2_scale2(spo2: float, on_oxygen: bool) -> int:
    if spo2 <= 83:
        return 3
    if spo2 <= 85:
        return 2
    if spo2 <= 87:
        return 1
    if spo2 <= 92 or not on_oxygen:
        return 0
    if spo2 <= 94:
        return 1
    if spo2 <= 96:
        return 2
    return 3


def score_supplemental_oxygen(on_oxygen: bool) -> int:
    return 2 if on_oxygen else 0


def score_systolic_bp(mmhg: float) -> int:
    if mmhg <= 90:
        return 3
    if mmhg <= 100:
        return 2
    if mmhg <= 110:
        return 1
    if mmhg <= 219:
        return 0
    return 3


def score_pulse(beats_per_min: float) -> int:
    if beats_per_min <= 40:
        return 3
    if beats_per_min <= 50:
        return 1
    if beats_per_min <= 90:
        return 0
    if beats_per_min <= 110:
        return 1
    if beats_per_min <= 130:
        return 2
    return 3


ACVPU = ("A", "C", "V", "P", "U")


def score_consciousness(acvpu: str) -> int:
    """A (alert) scores 0; C (new confusion), V (voice), P (pain), U scores 3.

    Only the five letters are accepted: free text such as "agitated" is not a
    level on the scale, so it raises rather than being guessed.
    """
    level = acvpu.strip().upper()
    if level not in ACVPU:
        raise ValueError(f"consciousness must be one of {ACVPU}, got {acvpu!r}")
    return 0 if level == "A" else 3


def score_temperature(celsius: float) -> int:
    if celsius <= 35.0:
        return 3
    if celsius <= 36.0:
        return 1
    if celsius <= 38.0:
        return 0
    if celsius <= 39.0:
        return 1
    return 2


# --- NEWS2 aggregate --------------------------------------------------------

NEWS2_FIELDS = (
    "respiration_rate",
    "spo2",
    "on_oxygen",
    "systolic_bp",
    "pulse",
    "consciousness",
    "temperature",
)


# Plain-English ways to name each observation, for example in an error message.
NEWS2_FIELD_NAMES = {
    "respiration_rate": ("respiration rate", "respiratory rate", "breathing rate"),
    "spo2": ("spo2", "oxygen saturation", "saturation", "sats"),
    "on_oxygen": ("on oxygen", "oxygen", "air or oxygen"),
    "systolic_bp": ("systolic bp", "systolic", "blood pressure"),
    "pulse": ("pulse", "heart rate"),
    "consciousness": ("consciousness", "acvpu"),
    "temperature": ("temperature", "temp"),
}


def names_observation(message: str, field: str) -> bool:
    """True if `message` names the NEWS2 observation `field`, by key or in words."""
    text = message.lower().replace("₂", "2")
    return field in text or any(name in text for name in NEWS2_FIELD_NAMES[field])


def news2_parameter_scores(vitals: dict) -> dict:
    """Score each NEWS2 parameter. Missing observations raise a ValueError.

    `vitals` is a plain dict with the keys in NEWS2_FIELDS and, optionally,
    "spo2_scale" set to 1 or 2.
    """
    missing = [field for field in NEWS2_FIELDS if vitals.get(field) is None]
    if missing:
        raise ValueError(f"cannot score NEWS2, missing: {', '.join(missing)}")
    if vitals.get("spo2_scale", 1) == 2:
        spo2_score = score_spo2_scale2(vitals["spo2"], vitals["on_oxygen"])
    else:
        spo2_score = score_spo2_scale1(vitals["spo2"])
    return {
        "respiration_rate": score_respiration_rate(vitals["respiration_rate"]),
        "spo2": spo2_score,
        "on_oxygen": score_supplemental_oxygen(vitals["on_oxygen"]),
        "systolic_bp": score_systolic_bp(vitals["systolic_bp"]),
        "pulse": score_pulse(vitals["pulse"]),
        "consciousness": score_consciousness(vitals["consciousness"]),
        "temperature": score_temperature(vitals["temperature"]),
    }


def news2_total(vitals: dict) -> int:
    return sum(news2_parameter_scores(vitals).values())


def news2_risk(vitals: dict) -> str:
    """Clinical risk band: "low", "low-medium", "medium" or "high"."""
    scores = news2_parameter_scores(vitals)
    total = sum(scores.values())
    if total >= 7:
        return "high"
    if total >= 5:
        return "medium"
    if 3 in scores.values():
        return "low-medium"
    return "low"
