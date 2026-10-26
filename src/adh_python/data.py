# SPDX-FileCopyrightText: 2026 Bradley Segal
# SPDX-License-Identifier: MIT

"""Synthetic patient data for the bootcamp.

Everything here is invented. No record corresponds to a real person. Data are
plain dicts and lists, the same structures students learn in the basics
notebook, so they can print and inspect anything they are given.
"""

from __future__ import annotations

import copy
import random

from adh_python import clinical

_SAMPLE_PATIENT = {
    "name": "Jordan Nguyen",
    "hospital_number": "RTH-102938",
    "age": 54,
    "pronouns": "they/them",
    "ward": "5B",
    "bed": 12,
    "consultant": "Dr Priya Patel",
    "diagnosis": "Community-acquired pneumonia",
    "height_m": 1.72,
    "weight_kg": 81.4,
    "allergies": ["Penicillin"],
    "medications": [
        "Metformin 1 g twice daily",
        "Ramipril 5 mg once daily",
        "Atorvastatin 20 mg once daily (withheld while on clarithromycin)",
        "Clarithromycin 500 mg orally twice daily",
    ],
    # One reading per observation round, oldest first.
    "observations": {
        "time": ["06:00", "10:00", "14:00", "18:00", "22:00", "02:00", "06:00"],
        "respiration_rate": [24, 22, 21, 20, 19, 18, 17],
        "spo2": [92, 93, 94, 94, 95, 96, 96],
        "on_oxygen": [True, True, True, True, False, False, False],
        "systolic_bp": [104, 108, 112, 118, 121, 124, 126],
        "pulse": [112, 106, 101, 96, 92, 88, 84],
        "consciousness": ["A", "A", "A", "A", "A", "A", "A"],
        "temperature": [38.6, 38.3, 37.9, 37.6, 37.3, 37.0, 36.8],
        "pain_score": [7, 6, 5, 4, 4, 3, 2],
    },
    "consults": ["Respiratory physiotherapy"],
    "outstanding_tasks": [
        "Chase blood culture results",
        "Reassess oxygen requirement when mobilising",
    ],
}


def sample_patient() -> dict:
    """Return a fresh copy of the sample patient, safe to modify."""
    return copy.deepcopy(_SAMPLE_PATIENT)


def latest_observations(patient: dict) -> dict:
    """The most recent value of each observation, as a single-round dict."""
    return {name: series[-1] for name, series in patient["observations"].items()}


_FIRST_NAMES = [
    "Amara",
    "Ben",
    "Chloe",
    "Dev",
    "Elena",
    "Femi",
    "Grace",
    "Hamza",
    "Isla",
    "Jun",
    "Kai",
    "Leah",
    "Mohammed",
    "Niamh",
    "Oscar",
    "Priya",
    "Rosa",
    "Sam",
]
_SURNAMES = [
    "Adeyemi",
    "Brown",
    "Chen",
    "Davies",
    "Evans",
    "Fraser",
    "Gupta",
    "Hughes",
    "Ibrahim",
    "Jones",
    "Khan",
    "Lewis",
    "Morgan",
    "Novak",
    "Okafor",
    "Patel",
]
# Diagnosis -> plausible age range on an acute medical ward.
_DIAGNOSES = {
    "Community-acquired pneumonia": (25, 92),
    "Exacerbation of COPD": (55, 90),
    "Urinary tract infection": (30, 95),
    "Cellulitis of the left leg": (30, 88),
    "Heart failure": (60, 95),
    "Acute kidney injury": (50, 92),
    "Diabetic ketoacidosis, resolving": (18, 45),
    "Fall, under investigation": (70, 96),
}


def _round_observations(
    rng: random.Random, unwell: float, hypercapnic: bool = False
) -> dict:
    """One plausible set of observations; `unwell` from 0 (well) to 1 (very unwell).

    Oxygen follows saturation, as it would on a ward: a patient whose SpO2 on
    air falls below the usual target is usually given oxygen, which brings
    their measured SpO2 back up. A patient with hypercapnic respiratory failure
    is on SpO2 scale 2 with a prescribed target of 88-92%.
    """
    on_air = round(rng.gauss(97.5 - 8 * unwell, 1.2))
    if hypercapnic:
        on_oxygen = rng.random() < 0.8
        spo2 = rng.randint(88, 92)  # within the prescribed target
    elif on_air < 94 and rng.random() < 0.85:
        on_oxygen = True
        spo2 = min(98, round(rng.gauss(95.5 - 3 * unwell, 1.2)))
    else:
        on_oxygen = False
        spo2 = min(100, on_air)
    return {
        "respiration_rate": round(rng.gauss(15 + 10 * unwell, 1.5)),
        "spo2": spo2,
        "on_oxygen": on_oxygen,
        "systolic_bp": round(rng.gauss(130 - 35 * unwell, 9)),
        "pulse": round(rng.gauss(74 + 40 * unwell, 7)),
        "consciousness": "A" if rng.random() > 0.2 * unwell**2 else "C",
        "temperature": round(rng.gauss(36.8 + 1.6 * unwell, 0.3), 1),
        "spo2_scale": 2 if hypercapnic else 1,
    }


# A typical acute medical ward: most patients score low, a few need closer
# review. (band, share of the ward, range of "unwell" to draw observations from)
_CASE_MIX = (
    ("low", 0.60, (0.0, 0.3)),
    ("low-medium", 0.15, (0.2, 0.5)),
    ("medium", 0.15, (0.4, 0.7)),
    ("high", 0.10, (0.6, 1.0)),
)


def _target_bands(rng: random.Random, n_patients: int) -> list[str]:
    bands = []
    for band, share, _ in _CASE_MIX:
        bands += [band] * max(1, round(share * n_patients))
    bands = bands[:n_patients] + ["low"] * (n_patients - len(bands))
    rng.shuffle(bands)
    return bands


def _observations_in_band(rng: random.Random, band: str, hypercapnic: bool) -> dict:
    """Draw observations until they fall in the requested NEWS2 risk band."""
    low, high = next(r for name, _, r in _CASE_MIX if name == band)
    while True:
        observations = _round_observations(rng, rng.uniform(low, high), hypercapnic)
        if clinical.news2_risk(observations) == band:
            return observations


def ward(n_patients: int = 12, seed: int = 2026) -> list[dict]:
    """A synthetic ward: a list of patient dicts with current observations.

    The same seed always gives the same ward, so every student sees the same
    patients and checkers can compare answers. Most patients score low on
    NEWS2; a few fall in each higher risk band. One patient with an
    exacerbation of COPD is on SpO2 scale 2.
    """
    rng = random.Random(seed)
    # Names come from their own generator, without repeats: two patients with
    # the same name on one ward list would confuse students (and staff).
    names = random.Random(seed).sample(
        [f"{first} {last}" for first in _FIRST_NAMES for last in _SURNAMES],
        n_patients,
    )
    bands = _target_bands(rng, n_patients)
    scale2_bed = next(
        (bed for bed, band in enumerate(bands, start=1) if band != "low"), None
    )
    patients = []
    for bed, band in enumerate(bands, start=1):
        hypercapnic = bed == scale2_bed
        if hypercapnic:
            diagnosis = "Exacerbation of COPD"
        else:
            diagnosis = rng.choice(
                [d for d in _DIAGNOSES if d != "Exacerbation of COPD"]
            )
        youngest, oldest = _DIAGNOSES[diagnosis]
        patients.append(
            {
                "name": names[bed - 1],
                "bed": bed,
                "age": rng.randint(youngest, oldest),
                "diagnosis": diagnosis,
                "observations": _observations_in_band(rng, band, hypercapnic),
            }
        )
    return patients
