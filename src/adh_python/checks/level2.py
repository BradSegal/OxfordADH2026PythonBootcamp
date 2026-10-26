# SPDX-FileCopyrightText: 2026 Bradley Segal
# SPDX-License-Identifier: MIT

"""Checkers for Level 2: strings and messages.

Each checker takes the inputs the student used as well as their answer, and
picks the hint that matches the most likely mistake in that answer.
"""

from __future__ import annotations

from adh_python.checks._core import (
    check_value,
    guard_checkers,
    is_placeholder,
    report,
    waiting,
)


def predict_message(prediction):
    expected = f"Bed {12}: {38.46:.1f}"
    if not isinstance(prediction, str):
        hint = 'Python prints text, so write your prediction in quotes, like "Bed 1: 36.0".'
    elif "{" in prediction:
        hint = "Python replaces each {...} with the value of the variable inside it."
    elif "38.46" in prediction:
        hint = ":.1f shows the number to one decimal place."
    elif "38.4" in prediction:
        hint = ":.1f rounds rather than cutting off, so 38.46 is shown as 38.5."
    elif prediction.strip().lower() == expected.lower():
        hint = "Nearly. Text outside the braces is printed exactly as written, spaces and capitals included."
    else:
        hint = "Text outside the braces is printed exactly as written; each {...} is replaced by its value."
    return check_value("Prediction", prediction, expected, hint=hint)


def patient_label(name, hospital_number, ward, bed, label):
    expected = f"{name} ({hospital_number}), ward {ward}, bed {bed}"
    if isinstance(label, str) and "{" in label:
        hint = "Your label shows the braces themselves. Did you forget the f before the opening quote?"
    elif isinstance(label, str) and (str(ward) not in label or str(bed) not in label):
        hint = "The ward or the bed is missing. Add each inside {} as the name is."
    else:
        hint = "Match the target exactly, including the commas and spaces."
    return check_value("Patient label", label, expected, hint=hint)


def tidy_name(raw_name, clean_name):
    expected = raw_name.strip().title()
    if clean_name == raw_name:
        hint = (
            "Your text has not changed. A method such as .strip() gives back a new"
            " string and leaves the old one alone, so store the result:"
            " clean_name = raw_name.strip()."
        )
    elif isinstance(clean_name, str) and clean_name != clean_name.strip():
        hint = "There are still spaces at the start or end. Use .strip()."
    elif isinstance(clean_name, str) and clean_name.lower() == expected.lower():
        hint = "The letters are right but the capitals are not. .title() gives each word a capital first letter."
    else:
        hint = "Chain the two methods: raw_name.strip().title()."
    return check_value("Tidy name", clean_name, expected, hint=hint)


def standard_hospital_number(raw_number, hospital_number):
    expected = raw_number.strip().upper().replace(" ", "-")
    if not isinstance(hospital_number, str):
        hint = "The hospital number should be text."
    elif hospital_number.startswith("-") or hospital_number.endswith("-"):
        hint = (
            "There is a dash at the start or end. The order of the methods"
            " matters: .strip() the outside spaces before you .replace() the"
            " space in the middle."
        )
    elif hospital_number != hospital_number.strip():
        hint = "There are still spaces at the start or end. Use .strip()."
    elif hospital_number != hospital_number.upper():
        hint = "Some letters are still lower case. Use .upper()."
    elif " " in hospital_number:
        hint = 'The space in the middle should be a dash: .replace(" ", "-").'
    else:
        hint = 'Use .strip(), then .upper(), then .replace(" ", "-").'
    return check_value("Hospital number", hospital_number, expected, hint=hint)


def blood_pressure(recorded, systolic, diastolic):
    name = "Systolic and diastolic"
    first, second = recorded.split("/")
    expected = (int(first), int(second))
    if is_placeholder(systolic) or is_placeholder(diastolic):
        return waiting(name)
    answer = (systolic, diastolic)
    if isinstance(systolic, str) or isinstance(diastolic, str):
        hint = 'These are still text, such as "128". Convert each piece with int().'
    elif any(type(value) is float for value in answer):
        return report(
            name,
            [
                f"expected {expected!r}, got {answer!r}. Hint: The problem asks"
                " for each pressure as a whole number, so convert with int(),"
                f" which gives {expected[0]}, rather than float(), which gives"
                f" {float(expected[0])}."
            ],
        )
    elif answer == expected[::-1]:
        hint = "Systolic and diastolic are swapped. Systolic comes first, before the slash: parts[0]."
    else:
        hint = 'Split on the slash with recorded.split("/"), then convert parts[0] and parts[1] with int().'
    return check_value(name, answer, expected, hint=hint)


def total_intake(first_ml, second_ml, total_ml):
    expected = int(first_ml) + int(second_ml)
    if isinstance(total_ml, str) and total_ml == str(first_ml) + str(second_ml):
        hint = (
            f'+ joined the two pieces of text ("{first_ml}" + "{second_ml}" is'
            f' "{total_ml}"). Convert each with int() before adding.'
        )
    elif isinstance(total_ml, str):
        hint = "Your total is text. Convert each volume with int() before adding."
    elif type(total_ml) is float:
        hint = (
            "The problem asks for whole millilitres, so convert with int(), which"
            f" gives {expected}, rather than float(), which gives {float(expected)}."
        )
    else:
        hint = "Convert each volume with int(), then add the two numbers."
    return check_value("Total intake", total_ml, expected, hint=hint, exact_type=True)


guard_checkers(globals())
