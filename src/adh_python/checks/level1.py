# SPDX-FileCopyrightText: 2026 Bradley Segal
# SPDX-License-Identifier: MIT

"""Checkers for Level 1: values, arithmetic and variables.

Each checker takes the inputs the student used as well as their answer, so the
check still works if a student changes the numbers to experiment.
"""

from __future__ import annotations

from adh_python import clinical
from adh_python.checks._core import (
    check_value,
    guard_checkers,
    is_placeholder,
    report,
)


def predict_dose(prediction):
    return check_value(
        "Prediction",
        prediction,
        105.0,
        hint="70 * 1.5 is 105. Python shows 105.0 because 1.5 is a decimal (float).",
    )


TARGET_WEIGHT_LB = 198


def weight_in_kg(weight_lb, weight_kg):
    if not is_placeholder(weight_lb) and weight_lb != TARGET_WEIGHT_LB:
        return report(
            "Weight in kg",
            [
                f"weight_lb is still {weight_lb!r}. Change it to"
                f" {TARGET_WEIGHT_LB}, then run the cell again."
            ],
        )
    return check_value(
        "Weight in kg",
        weight_kg,
        clinical.lb_to_kg(TARGET_WEIGHT_LB),
        hint="Divide pounds by 2.20462. Multiplying gives a number that is too big.",
    )


def temperature_in_celsius(temp_f, temp_c):
    return check_value(
        "Temperature in °C",
        temp_c,
        clinical.fahrenheit_to_celsius(temp_f),
        hint=(
            "Subtract 32 first then multiply by 5 / 9. Brackets control the "
            "order of operations."
        ),
    )


def paracetamol_dose(weight_kg, dose_mg):
    return check_value(
        "Paracetamol dose",
        dose_mg,
        clinical.weight_based_dose_mg(weight_kg, 15),
        hint="The dose is weight in kg multiplied by 15 mg/kg.",
    )


def bmi_from_cm(weight_kg, height_cm, bmi):
    return check_value(
        "BMI",
        bmi,
        clinical.bmi(weight_kg, height_cm / 100),
        hint=("Convert centimetres to metres first (divide by 100) then square it."),
    )


FLUID_IN_ML = 500 + 250 + 700
FLUID_OUT_ML = 400 + 700


def fluid_balance(balance_ml):
    expected = FLUID_IN_ML - FLUID_OUT_ML
    if balance_ml == FLUID_IN_ML + FLUID_OUT_ML:
        hint = "You added the outputs too. Urine out should use -= (subtract)."
    elif balance_ml == -expected:
        hint = "The sign is reversed: balance is total in minus total out."
    elif balance_ml == FLUID_IN_ML:
        hint = "You have the intakes; now subtract each output with -=."
    else:
        hint = "Add each intake with += and subtract each output with -=."
    return check_value("Fluid balance", balance_ml, expected, hint=hint)


guard_checkers(globals())
