# SPDX-FileCopyrightText: 2026 Bradley Segal
# SPDX-License-Identifier: MIT

"""Checkers for the MedVision lab.

The model's replies differ between a GPU run, the saved replies and the tiny
test model, and judging them is the student's job. So these checkers check the
shape of what students record (the right images, the right keys, True or
False rather than text) and their arithmetic, never the clinical judgement.
"""

from __future__ import annotations

from adh_python.checks._core import (
    article,
    guard_checkers,
    is_number,
    is_placeholder,
    near,
    report,
    waiting,
)
from adh_python.imaging.images import IMAGES

RESULT_KEYS = ("image", "model_finding", "agrees")


def _bool_problem(label: str, value) -> str | None:
    if isinstance(value, bool):
        return None
    if isinstance(value, str):
        return (
            f"{label} is the text {value!r}. Use True or False without quotes, "
            "so Python can count them."
        )
    return f"{label} should be True or False, got {value!r}."


def failure_modes(notes):
    name = "Failure modes"
    if is_placeholder(notes):
        return waiting(name)
    if not isinstance(notes, dict):
        return report(name, [f"expected a dict, got {article(type(notes).__name__)}."])
    if any(is_placeholder(value) for value in notes.values()):
        return waiting(name)
    problems = []
    for key in ("invented_pneumothorax", "invented_mass"):
        if key not in notes:
            problems.append(f"the dict needs the key {key!r}.")
        elif problem := _bool_problem(f"notes[{key!r}]", notes[key]):
            problems.append(problem)
    return report(name, problems)


def evaluation_table(results):
    name = "Evaluation table"
    if is_placeholder(results):
        return waiting(name)
    if not isinstance(results, list):
        return report(
            name, [f"expected a list of dicts, got {article(type(results).__name__)}."]
        )
    if any(
        isinstance(row, dict) and any(is_placeholder(v) for v in row.values())
        for row in results
    ):
        return waiting(name)
    problems = []
    seen = []
    for index, row in enumerate(results):
        if not isinstance(row, dict):
            problems.append(f"item {index} should be a dict, got {row!r}.")
            continue
        missing = [key for key in RESULT_KEYS if key not in row]
        if missing:
            problems.append(
                f"item {index} is missing {', '.join(map(repr, missing))}. "
                "Keys are case-sensitive: use exactly 'image', 'model_finding' "
                "and 'agrees'."
            )
            continue
        if row["image"] not in IMAGES:
            problems.append(
                f"item {index}: {row['image']!r} is not an image name; "
                f"use one of {sorted(IMAGES)}."
            )
        seen.append(row["image"])
        finding = row["model_finding"]
        if not isinstance(finding, str) or not finding.strip():
            problems.append(
                f"item {index}: 'model_finding' should be a few words of text "
                "saying what the model reported."
            )
        if problem := _bool_problem(f"item {index}: 'agrees'", row["agrees"]):
            problems.append(problem)
    repeated = sorted({image for image in seen if seen.count(image) > 1})
    if repeated:
        problems.append(f"{', '.join(repeated)} appears more than once.")
    left_out = [image for image in IMAGES if image not in seen]
    if left_out:
        problems.append(
            f"no row for {', '.join(left_out)}. An evaluation that drops the "
            "difficult cases looks better than it is: include every image."
        )
    return report(name, problems)


def agreement(results, n_agree, percent):
    name = "Agreement"
    if is_placeholder(n_agree) or is_placeholder(percent):
        return waiting(name)
    try:
        table_ready = len(results) > 0 and all(
            isinstance(row["agrees"], bool) for row in results
        )
    except (TypeError, KeyError):
        table_ready = False
    if not table_ready:
        return report(
            name, ["finish the evaluation table above first, then run this cell."]
        )
    expected_n = sum(1 for row in results if row["agrees"])
    expected_percent = 100 * expected_n / len(results)
    problems = []
    if n_agree != expected_n:
        problems.append(
            f"{expected_n} of your {len(results)} rows have 'agrees' set to True, "
            f"but n_agree is {n_agree!r}. Add 1 only when row['agrees'] is True."
        )
    if not is_number(percent) or percent != percent:  # only NaN differs from itself
        problems.append(
            f"percent should be a number, got {percent!r}. Work it out from "
            "n_agree and len(results), then multiply by 100."
        )
    elif not 0 <= percent <= 100:  # also catches infinity
        problems.append(
            f"percent is {percent!r}, but a percentage lies between 0 and 100. "
            "Divide by the number of rows, len(results), then multiply by 100."
        )
    elif not near(percent, expected_percent, tolerance=0.1):
        hint = (
            " Multiply by 100 to turn a proportion into a percentage."
            if near(100 * percent, expected_percent, tolerance=0.1)
            else " Divide by the number of rows, len(results), then multiply by 100."
        )
        problems.append(
            f"percent should be {expected_percent:.0f}, got {percent!r}.{hint}"
        )
    return report(name, problems)


guard_checkers(globals())
