# SPDX-FileCopyrightText: 2026 Bradley Segal
# SPDX-License-Identifier: MIT

"""Checkers for Level 5: dictionaries and records.

Each checker takes the data the student worked on as well as their answer, so
the check still works if a student changes the inputs to experiment.
"""

from __future__ import annotations

from adh_python import data
from adh_python.checks._core import check_value, guard_checkers, report


def predict_record_length(prediction):
    hint = "Count the keys after both changes: name, ward, bed and consultant."
    if prediction == 5:
        hint = (
            "Assigning to a key that already exists, like 'bed', replaces its"
            " value. It does not add a second 'bed'."
        )
    elif prediction == 3:
        hint = "Assigning to a key that does not exist yet, like 'consultant', adds it."
    return check_value("Prediction", prediction, 4, hint=hint)


TRANSFER = {"ward": "7A", "bed": 3, "consultant": "Dr Aisha Rahman"}


def _quoted(keys):
    return ", ".join(repr(key) for key in keys)


def _differences(new, old, changing, label, example):
    """Problems with `new` apart from the keys in `changing`, compared with `old`.

    A record that was rebuilt or replaced, rather than changed one key at a
    time, loses or alters entries nobody asked to change. `label` names the
    record in the feedback and `example` shows how to change one key.
    """
    added = [key for key in new if key not in old]
    lost = [key for key in old if key not in new]
    altered = [
        key
        for key in old
        if key in new and key not in changing and new[key] != old[key]
    ]
    problems = []
    if added:
        problems.append(
            f"{label} has a new key {added[0]!r}. Keys must be spelled exactly as"
            " they already are, capitals included. Print .keys() to see them."
        )
    if lost:
        problems.append(
            f"{label} has lost {_quoted(lost)}. Change one key at a time,"
            f" for example {example}, rather than replacing the whole"
            " dictionary, so everything else is kept."
        )
    if altered:
        problems.append(
            f"in {label}, {_quoted(altered)} changed as well, but only"
            f" {_quoted(changing)} should. Run the whole cell again to start from"
            " the original record."
        )
    return problems


def transfer(patient):
    name = "Updated record"
    if not isinstance(patient, dict):
        return check_value(name, patient, TRANSFER)
    problems = _differences(
        patient, data.sample_patient(), TRANSFER, "the record", 'patient["ward"] = "7A"'
    )
    if problems:
        return report(name, problems)
    actual = {key: patient[key] for key in TRANSFER}
    hint = "Three things changed: the ward, the bed and the consultant."
    if isinstance(actual["bed"], str):
        hint = 'Bed numbers are stored as numbers: write 3, not "3".'
    elif actual["ward"] == "5B":
        hint = 'The ward is still 5B. Update patient["ward"] as well as the bed.'
    return check_value(name, actual, TRANSFER, hint=hint)


def allergy_check(drug_classes, allergies, new_drug, drug_class, alert):
    expected_class = drug_classes.get(new_drug)
    class_hint = "Look the drug up in the table with drug_classes[new_drug]."
    if drug_class == new_drug:
        class_hint = (
            "drug_class holds the drug's own name. Look up the class it belongs"
            " to with drug_classes[new_drug]."
        )
    class_ok = check_value("Drug class", drug_class, expected_class, hint=class_hint)

    expected_alert = expected_class in allergies
    if isinstance(alert, str):
        alert_hint = "Use the True or False that `in` gives you, not the text 'True'."
    elif expected_alert:
        alert_hint = (
            "This allergy is recorded as a class ('Penicillin'), so the drug's"
            " own name is not in the list. Check whether drug_class is in the"
            " allergy list."
        )
    else:
        alert_hint = (
            "This drug's class is not in the allergy list, so there should be"
            " no alert. Check drug_class, not the drug name."
        )
    alert_ok = check_value("Allergy alert", alert, expected_alert, hint=alert_hint)
    return class_ok and alert_ok


def oxygen_beds(patients, beds):
    expected = [p["bed"] for p in patients if p["observations"]["on_oxygen"]]
    hint = (
        'For each patient, look inside patient["observations"] for'
        ' "on_oxygen" and keep the bed number when it is True.'
    )
    if isinstance(beds, list) and beds:
        if isinstance(beds[0], dict):
            hint = 'Append the bed number, patient["bed"], not the whole patient.'
        elif isinstance(beds[0], str):
            hint = 'The question asks for bed numbers, patient["bed"], not names.'
        elif len(beds) == len(patients):
            hint = "You kept every patient. Add an if so you keep only those on oxygen."
        elif len(beds) == 1 and len(expected) > 1:
            hint = (
                "Only one bed was kept. Create the empty list once, before the"
                " loop, not inside it."
            )
    elif beds == []:
        hint = (
            'Your list is empty. Loop over patients and append patient["bed"]'
            ' when patient["observations"]["on_oxygen"] is True. on_oxygen is'
            ' already True or False; comparing it with the text "True" never'
            " matches."
        )
    return check_value("Beds on oxygen", beds, expected, hint=hint)


def _is_count(value):
    return isinstance(value, int) and not isinstance(value, bool)


def diagnosis_counts(patients, counts):
    expected = {}
    for patient in patients:
        diagnosis = patient["diagnosis"]
        expected[diagnosis] = expected.get(diagnosis, 0) + 1
    hint = "Each patient should add 1 to the count for their diagnosis."
    if isinstance(counts, dict):
        values = list(counts.values())
        if not counts:
            hint = (
                "counts is still empty. Inside the loop, set counts[diagnosis]"
                " to counts.get(diagnosis, 0) + 1."
            )
        elif not all(_is_count(v) for v in values):
            hint = "Each value in counts should be a whole number: how many patients."
        elif all(v == 1 for v in values) and len(counts) < len(patients):
            hint = (
                "Every count is 1. Setting counts[diagnosis] = 1 starts again each"
                " time; add 1 to the count so far with counts.get(diagnosis, 0) + 1."
            )
        elif sum(values) != len(patients):
            hint = (
                f"Your counts add up to {sum(values)}, but there are"
                f" {len(patients)} patients. Each patient should be counted once."
            )
    return check_value("Diagnosis counts", counts, expected, hint=hint)


def oxygen_started(patients, bed, spo2, seed=2026):
    """The patient in `bed` is now on oxygen; nobody else's record should change."""
    name = "Ward record"
    if not isinstance(patients, list) or not all(isinstance(p, dict) for p in patients):
        return report(
            name,
            [
                "patients should be the list of patient dicts from"
                f" data.ward(seed={seed}). Run the whole cell again."
            ],
        )
    original = data.ward(n_patients=len(patients), seed=seed)
    targets = [p for p in patients if p.get("bed") == bed]
    if not targets:
        return report(name, [f"there is no patient in bed {bed} in patients."])

    wrong = [
        new.get("bed")
        for new, old in zip(patients, original, strict=True)
        if new.get("bed") != bed and new != old
    ]
    if wrong:
        hint = f"Only the patient in bed {bed} should change."
        if wrong[-1] == patients[-1].get("bed"):
            hint = (
                f"The update went to bed {wrong[-1]}, the last patient in the list."
                " After a loop ends, `patient` still holds the last patient it"
                " visited. Move the update inside the if, so it happens only for"
                f" bed {bed}."
            )
        elif isinstance(bed, int) and wrong[0] == bed + 1:
            hint = (
                f"Bed {wrong[0]} changed. List positions start at 0, so position"
                f" {bed} is bed {bed + 1}. Find the patient by their bed number."
            )
        return check_value("Other beds changed", wrong, [], hint=hint)

    observations = targets[0].get("observations")
    if not isinstance(observations, dict):
        return report(name, [f'bed {bed}\'s "observations" should still be a dict.'])
    before_patient = next((o for o in original if o["bed"] == bed), {})
    before = before_patient.get("observations", {})
    changing = ("on_oxygen", "spo2")
    example = 'patient["observations"]["spo2"] = new_spo2'
    misplaced = [key for key in changing if key in targets[0]]
    if misplaced:
        return report(
            name,
            [
                f"{_quoted(misplaced)} went into the patient record itself. They"
                f" belong inside the observations: {example}."
            ],
        )
    problems = _differences(
        targets[0], before_patient, ("observations",), f"bed {bed}'s record", example
    ) + _differences(
        observations, before, changing, f"bed {bed}'s observations dictionary", example
    )
    if problems:
        return report(name, problems)
    actual = {key: observations[key] for key in changing}
    hint = 'Update both on_oxygen and spo2 inside patient["observations"].'
    if actual == {"on_oxygen": before.get("on_oxygen"), "spo2": before.get("spo2")}:
        hint = f"Bed {bed}'s record has not changed. Do the update inside the if."
    elif isinstance(actual["on_oxygen"], str):
        hint = 'on_oxygen should be True, not the text "True".'
    return check_value(
        f"Bed {bed} observations",
        actual,
        {"on_oxygen": True, "spo2": spo2},
        hint=hint,
    )


guard_checkers(globals())
