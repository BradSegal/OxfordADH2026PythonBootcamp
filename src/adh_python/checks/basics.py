# SPDX-FileCopyrightText: 2026 Bradley Segal
# SPDX-License-Identifier: MIT

"""Checkers for the orientation (00) and Python basics walkthrough (01).

The walkthrough tries are small, one idea each. Each checker takes the inputs
the student used as well as their answer, and picks the hint that names the
mistake their answer suggests.
"""

from __future__ import annotations

from adh_python import data
from adh_python.checks._core import (
    Case,
    check_function,
    check_value,
    guard_checkers,
    is_number,
)

# --- 00 Colab orientation ---------------------------------------------------


def weekly_hours(hours):
    if hours == 3 + 12.5:
        hint = "You added. Use * to multiply: three shifts of 12.5 hours is 3 * 12.5."
    else:
        hint = "Replace the ... with 3 * 12.5, then run the cell again."
    return check_value("Hours worked", hours, 3 * 12.5, hint=hint)


def error_name(answer):
    if isinstance(answer, type):
        hint = 'Put the name in quotes, like "NameError", so Python treats it as text.'
    elif answer == "NameError":
        hint = "NameError was the first example. Which word starts the last line this time?"
    elif isinstance(answer, str) and answer.strip().lower() == "typeerror":
        hint = "Python names are exact: copy the capitals and leave out any spaces."
    else:
        hint = "Read the last line of the error message: the word before the colon."
    return check_value("Error name", answer, "TypeError", hint=hint)


# --- 01 Section 1: variables and strings ------------------------------------


def pulse_fall(first_pulse, latest_pulse, fall):
    if fall == latest_pulse - first_pulse and fall != 0:
        hint = (
            "Your answer is negative which means that your subtraction is "
            "the wrong way round. You need to take the latest reading away "
            "from the first."
        )
    else:
        hint = "Subtract one variable from the other: first_pulse - latest_pulse."
    return check_value("Fall in pulse", fall, first_pulse - latest_pulse, hint=hint)


def bed_label(ward, bed, label):
    expected = f"Ward {ward}, bed {bed}"
    if not isinstance(label, str):
        return check_value(
            "Bed label", label, expected, hint="Build it with an f-string."
        )
    label = label.strip()  # spaces before or after the label do no harm

    def letters(text):
        return "".join(text.split()).replace(",", "")

    if "{" in label:
        hint = (
            "The curly brackets were printed as they are. Put an f just before"
            ' the opening quote: f"Ward {ward}, bed {bed}".'
        )
    elif label.lower() == expected.lower():
        hint = f"Nearly. Match the capitals exactly, as in {expected}."
    elif letters(label) == letters(expected):
        hint = (
            "The words are right but the punctuation or spaces are not. Copy the"
            " target exactly: a comma after the ward, then a space, then bed."
        )
    elif expected in label:
        hint = (
            f"Your label has extra text. It should be exactly {expected},"
            " with nothing before or after it."
        )
    else:
        hint = 'Build it with an f-string: f"Ward {ward}, bed {bed}".'
    return check_value("Bed label", label, expected, hint=hint)


# --- 01 Section 2: lists ----------------------------------------------------


def latest_reading(readings, latest):
    if isinstance(latest, list):
        hint = "That is the whole list. Pick one reading with square brackets."
    elif len(readings) > 1 and latest == readings[0]:
        hint = (
            "This is the first (oldest) reading as Python counts from 0. The "
            "last reading is [-1]."
        )
    elif len(readings) > 1 and latest == readings[-2]:
        hint = "That is one before the last. The last reading is [-1]."
    else:
        hint = "Use the list name followed by [-1] to get the last reading."
    return check_value("Latest temperature", latest, readings[-1], hint=hint)


def appended_reading(pulse_readings, new_pulse):
    original = data.sample_patient()["observations"]["pulse"]
    expected = original + [new_pulse]
    if pulse_readings is None:
        hint = (
            ".append changes the list itself and returns None, so do not assign"
            " its result. Write pulse_readings.append(new_pulse) on its own line."
        )
    elif not isinstance(pulse_readings, list):
        hint = (
            "pulse_readings should still be the list of readings."
            " Add to it with pulse_readings.append(new_pulse) on its own line."
        )
    elif pulse_readings == original:
        hint = "The list has not changed. Add the reading with pulse_readings.append(new_pulse)."
    elif pulse_readings and pulse_readings[-1] == [new_pulse]:
        hint = "You added a list inside the list. Use .append(new_pulse), without square brackets."
    elif len(pulse_readings) == len(original) and pulse_readings[-1] == new_pulse:
        hint = (
            "You replaced the last reading. .append adds a new reading"
            " to the end and keeps all the others."
        )
    elif pulse_readings == expected + [new_pulse]:
        hint = "The new reading is there twice. Use .append once."
    else:
        hint = "Use pulse_readings.append(new_pulse) to add one reading at the end."
    return check_value("Pulse readings", pulse_readings, expected, hint=hint)


# --- 01 Section 3: dictionaries ---------------------------------------------


def moved_bed(patient, new_bed):
    current = patient.get("bed") if isinstance(patient, dict) else None
    if isinstance(current, str) and current == str(new_bed):
        hint = (
            f"Quotes make {new_bed} into text. Store the number itself, without quotes."
        )
    else:
        hint = (
            'Change the value inside the dictionary: patient["bed"] = new_bed.'
            " Making a new variable called bed leaves the dictionary unchanged."
        )
    return check_value("Bed in the patient record", current, new_bed, hint=hint)


def spo2_series(patient, series):
    observations = patient["observations"]
    if series == observations:
        hint = 'That is all of the observations. Add a second [ ] with the key "spo2".'
    elif is_number(series):
        hint = "That is a single reading. Stop after the second [ ] to keep the whole list."
    else:
        hint = 'Look up "observations" first, then "spo2" inside it: two pairs of [ ].'
    return check_value("SpO2 readings", series, observations["spo2"], hint=hint)


# --- 01 Section 4: loops and decisions --------------------------------------


def _trend(previous, latest):
    if latest > previous:
        return "rising"
    if latest < previous:
        return "falling"
    return "steady"


def pulse_trend(previous_pulse, latest_pulse, trend):
    expected = _trend(previous_pulse, latest_pulse)
    opposite = {"rising": "falling", "falling": "rising"}.get(expected)
    if (
        isinstance(trend, str)
        and trend.strip().lower() == expected
        and trend != expected
    ):
        hint = f'Use exactly "{expected}": lower case, no spaces.'
    elif trend == opposite:
        hint = (
            "The comparison is the wrong way round. If latest_pulse is greater"
            ' than previous_pulse (latest_pulse > previous_pulse), it is "rising".'
        )
    elif expected == "steady":
        hint = 'The readings are equal, so the answer is "steady". This is the else branch.'
    else:
        hint = "Compare latest_pulse with previous_pulse using > and <."
    return check_value("Pulse trend", trend, expected, hint=hint)


def rounds_on_oxygen(on_oxygen, count):
    expected = on_oxygen.count(True)
    if count == len(on_oxygen) and expected != len(on_oxygen):
        hint = (
            "You counted every round. Indent the += line under the if,"
            " so it runs only when needed is True."
        )
    elif count == len(on_oxygen) - expected and expected != len(on_oxygen) - expected:
        hint = "You counted the rounds off oxygen. Count the True values instead."
    elif count == 0:
        hint = (
            "The count never went up. Inside the if, add 1 with rounds_on_oxygen += 1."
        )
    else:
        hint = "Start at 0 and add 1 each time needed is True."
    return check_value("Rounds on oxygen", count, expected, hint=hint)


# --- 01 Section 5: functions ------------------------------------------------


def _ellipsis_line_as_placeholder(function):
    """Report a handover line still built from the starter's ... as not attempted.

    The starter's f-string turns `...` into the text "Ellipsis", so the student's
    function returns a string rather than `...` itself. Each case still calls the
    student's function exactly once.
    """

    def call(patient):
        line = function(patient)
        if isinstance(line, str) and "Ellipsis" in line:
            return ...
        return line

    return call


def average(function):
    any_length = "Divide by len(readings), so it works for any number of readings."
    cases = [
        Case(([37.0, 38.0],), 37.5),
        Case(([112, 106, 101, 96, 92, 88, 84],), 97.0),
        Case(([4, 6, 8, 2],), 5.0, hint=any_length),
        Case(([36.8],), 36.8, hint=any_length),
    ]
    return check_function("average", function, cases)


def handover_line(function):
    use_parameter = (
        "Look each value up in the parameter `patient`, not in `jordan`,"
        " so the function works for every patient."
    )
    first_hint = (
        'Look up bed and diagnosis in patient, as name does: patient["bed"].'
        " Check the comma, the colon and the spaces match the example."
    )
    jordan = data.sample_patient()
    patients = [
        {key: jordan[key] for key in ("name", "bed", "diagnosis")},
        {"name": "Amara Okafor", "bed": 3, "diagnosis": "Cellulitis of the left leg"},
        {"name": "Ben Hughes", "bed": 7, "diagnosis": "Exacerbation of COPD"},
    ]
    cases = [
        Case(
            (patient,),
            f"{patient['name']}, bed {patient['bed']}: {patient['diagnosis']}",
            hint=use_parameter if index else first_hint,
        )
        for index, patient in enumerate(patients)
    ]
    if callable(function):
        function = _ellipsis_line_as_placeholder(function)
    return check_function("handover_line", function, cases)


guard_checkers(globals())
