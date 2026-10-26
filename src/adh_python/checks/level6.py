# SPDX-FileCopyrightText: 2026 Bradley Segal
# SPDX-License-Identifier: MIT

"""Checkers for Level 6: functions and decomposition (building NEWS2).

Function checkers call the student's function on boundary cases and compare
the answers with the reference rules in adh_python.clinical, so no threshold
is restated here.
"""

from __future__ import annotations

from adh_python import clinical, data
from adh_python.checks._core import (
    Case,
    CheckResult,
    article,
    check_function,
    check_value,
    guard_checkers,
    is_placeholder,
    report,
    waiting,
)

# All seven observations in the range that scores 0.
NORMAL = {
    "respiration_rate": 16,
    "spo2": 97,
    "on_oxygen": False,
    "systolic_bp": 120,
    "pulse": 70,
    "consciousness": "A",
    "temperature": 37.0,
}


def _observations(**changes):
    return {**NORMAL, **changes}


def _scale1(observations):
    """The same observations scored on SpO2 scale 1."""
    return {**observations, "spo2_scale": 1}


def _scale1_ward(patients):
    return [{**p, "observations": _scale1(p["observations"])} for p in patients]


# --- Problem 6.1 -------------------------------------------------------------


def predict_return(prediction):
    hint = (
        "The function prints 4000 on the screen, but it has no `return`, so it"
        " hands back None. Type None without quotes."
    )
    if prediction == "None":
        hint = "None is a value of its own, like True. Type it without quotes."
    return check_value("Prediction", prediction, None, hint=hint)


# --- Problems 6.2 and 6.3: single-parameter scorers ------------------------


def _boundary_hint(value):
    return (
        f"{value} is the top of its band on the chart, and bands include their"
        " top number. Check <= versus <."
    )


def score_pulse(function):
    hints = {v: _boundary_hint(v) for v in (40, 50, 90, 130)}
    hints[91] = "91-110 is a band of its own that scores 1. Did you add it?"
    hints[110] = hints[91]
    cases = [
        Case((v,), clinical.score_pulse(v), hints.get(v, ""))
        for v in (70, 30, 40, 41, 50, 51, 90, 91, 110, 111, 130, 131, 150)
    ]
    return check_function("score_pulse", function, cases)


def score_temperature(function):
    cases = [
        Case(
            (v,),
            clinical.score_temperature(v),
            _boundary_hint(v) if v in (35.0, 36.0, 38.0, 39.0) else "",
        )
        for v in (37.0, 34.0, 35.0, 35.1, 36.0, 36.1, 38.0, 38.1, 39.0, 39.1, 40.0)
    ]
    return check_function("score_temperature", function, cases)


# --- Problem 6.4: composing the scorers --------------------------------------


def _observation_cases():
    cases = [
        _observations(),
        data.latest_observations(data.sample_patient()),
        _observations(
            respiration_rate=8,
            spo2=91,
            on_oxygen=True,
            systolic_bp=90,
            pulse=131,
            consciousness="V",
            temperature=39.1,
        ),
        _observations(respiration_rate=22, pulse=95, temperature=38.0),
    ]
    cases += [p["observations"] for p in data.ward(seed=2026)]
    return [_scale1(obs) for obs in cases]


SCORES_HINT = (
    "Return a dict with one score per observation, using the same keys as the"
    " observations. If only pulse or temperature is wrong, make sure"
    " score_pulse and score_temperature pass their own checks first."
)


# The two ways an observation can be missing, each as (how the problem
# describes it, how the incomplete record is made, the hint for that form).
_MISSING_FORMS = (
    (
        "missing",
        lambda field: {k: v for k, v in NORMAL.items() if k != field},
        "check every field is present before scoring, and raise ValueError"
        " naming the one that is missing.",
    ),
    (
        "set to None",
        lambda field: {**NORMAL, field: None},
        "None means nobody recorded it, so treat it as missing:"
        " `observations.get(field) is None` is True for a missing key and for"
        " None.",
    ),
)


def _missing_problems(name, function, fields):
    """Problems with how `function` handles each field, absent or None.

    Returns None if the function still returns the `...` placeholder, so an
    unattempted scaffold is reported as not attempted rather than as wrong.
    """
    problems = []
    for form, incomplete, hint in _MISSING_FORMS:
        for field in fields:
            try:
                result = function(incomplete(field))
            except ValueError as error:
                if not clinical.names_observation(str(error), field):
                    problems.append(
                        f"with {field!r} {form}, the ValueError said"
                        f" {str(error)!r}, which does not say which observation"
                        f" is missing. Hint: put its name in the message, for"
                        f' example f"{{field}} is missing", so whoever reads it'
                        " knows what to record."
                    )
                continue
            except Exception as error:  # report any student error in plain English
                problems.append(
                    f"with {field!r} {form}, {name} raised"
                    f" {type(error).__name__}: {error}. Hint: {hint}"
                )
                continue
            if is_placeholder(result):
                return None
            problems.append(
                f"with {field!r} {form}, {name} did not stop. Hint: a missing"
                f" observation must raise ValueError, not be scored quietly; {hint}"
            )
    return problems


def _check_missing(name, function, fields=clinical.NEWS2_FIELDS):
    label = f"{name} with a missing observation"
    if is_placeholder(function):
        return waiting(label)
    if not callable(function):
        return report(
            label, [f"expected a function, got {article(type(function).__name__)}."]
        )
    problems = _missing_problems(name, function, fields)
    if problems is None:  # the scaffold is untouched; check_function said so
        return CheckResult(False)
    return report(label, problems)


def news2_scores(function):
    cases = [
        Case((obs,), clinical.news2_parameter_scores(obs), SCORES_HINT)
        for obs in _observation_cases()
    ]
    scored = check_function("news2_scores", function, cases)
    loud = _check_missing("news2_scores", function)
    return scored and loud


def news2_total(function):
    cases = [
        Case(
            (obs,),
            clinical.news2_total(obs),
            "Add up the scores news2_scores gives you: sum(scores.values()).",
        )
        for obs in _observation_cases()
    ]
    totalled = check_function("news2_total", function, cases)
    loud = _check_missing("news2_total", function)
    return totalled and loud


# --- Problem 6.5: the risk band ----------------------------------------------


def _returns_placeholder(function, args):
    """True if the function still returns the scaffold's `...` placeholder."""
    try:
        return is_placeholder(function(*args))
    except Exception:  # an attempted function may raise; that is not a placeholder
        return False


SINGLE_THREE = "A score of 3 in any one parameter makes the risk at least low-medium."
TOTAL_FIRST = "Check the total first: a total of 5 or more outranks a single 3."
RISK_CASES = [
    (_observations(), ""),
    (
        _observations(respiration_rate=22, pulse=95),  # 2 + 1
        "A total of 3 made of smaller scores is still low; low-medium needs one"
        " parameter scoring 3.",
    ),
    (_observations(consciousness="C"), SINGLE_THREE),
    (_observations(consciousness="C", pulse=95), SINGLE_THREE),  # 4 with a 3
    (
        _observations(respiration_rate=22, on_oxygen=True, pulse=95),  # 5
        "A total of 5 is medium: use >= 5, not > 5.",
    ),
    (_observations(consciousness="C", respiration_rate=22), TOTAL_FIRST),  # 5
    (
        _observations(respiration_rate=22, on_oxygen=True, spo2=94, pulse=95),  # 6
        "A total of 6 is medium.",
    ),
    (
        _observations(respiration_rate=22, on_oxygen=True, spo2=93, pulse=95),  # 7
        "A total of 7 is high: use >= 7, not > 7.",
    ),
    (
        _observations(consciousness="C", respiration_rate=22, on_oxygen=True),  # 7
        "Check for high (7 or more) before the single-3 rule.",
    ),
]


def news2_risk(function):
    cases = [
        Case((_scale1(obs),), clinical.news2_risk(obs), hint)
        for obs, hint in RISK_CASES
    ]
    banded = check_function("news2_risk", function, cases)
    if is_placeholder(function) or not callable(function):
        return banded
    if not banded and _returns_placeholder(function, (_scale1(NORMAL),)):
        return banded  # not attempted yet: no verdict on the docstring either
    documented = report(
        "news2_risk docstring",
        []
        if (function.__doc__ or "").strip()
        else [
            "there is no docstring. Hint: add one line in triple quotes just"
            " under the def, saying what the function returns."
        ],
    )
    return banded and documented


# --- Problem 6.6: the watch list ---------------------------------------------


def _expected_watch_list(patients):
    entries = [
        {
            "bed": p["bed"],
            "name": p["name"],
            "news2": clinical.news2_total(p["observations"]),
            "risk": clinical.news2_risk(p["observations"]),
        }
        for p in patients
    ]
    entries = [e for e in entries if e["risk"] != "low"]
    return sorted(entries, key=lambda e: e["news2"], reverse=True)


def _patient(bed, name, **changes):
    return {"bed": bed, "name": name, "observations": _scale1(_observations(**changes))}


WATCH_KEYS = {"bed", "name", "news2", "risk"}
SORT_HINT = (
    "Put the highest NEWS2 first: sorted(watch_list, key=news2_of, reverse=True)."
)


def _same_entry(actual, expected):
    """Entries match field by field; True is not accepted as 1."""
    return all(
        type(actual[key]) is type(expected[key]) and actual[key] == expected[key]
        for key in WATCH_KEYS
    )


def _unmatched(entries, others):
    """The entries with no matching partner in `others`, as for a multiset."""
    remaining = list(others)
    left_over = []
    for entry in entries:
        match = next((o for o in remaining if _same_entry(entry, o)), None)
        if match is None:
            left_over.append(entry)
        else:
            remaining.remove(match)
    return left_over


def _watch_problem(actual, expected):
    """What is wrong with one returned watch list, or "" if it is right.

    The entries are compared as a collection first, so patients with equal
    scores may come in either order; the order is then checked on its own.
    """
    if not isinstance(actual, list):
        return f"returned {type(actual).__name__}, not a list of entries."
    if not all(isinstance(e, dict) for e in actual):
        return "each entry should be a dict with the keys bed, name, news2 and risk."
    for entry in actual:
        if set(entry) != WATCH_KEYS:
            return (
                "each entry needs exactly the keys bed, name, news2 and risk;"
                f" one has {sorted(entry, key=str)}."
            )
    missing = _unmatched(expected, actual)
    extra = _unmatched(actual, expected)
    if missing or extra:
        if not actual:
            return (
                f"your list is empty, but {len(expected)} patient(s) should be on"
                ' it. Hint: for each patient whose risk is not "low", append an'
                " entry with the four keys."
            )
        if any(e["risk"] == "low" for e in extra):
            return 'it includes a patient whose risk is "low"; leave those out.'
        if any(e["risk"] == "low-medium" for e in missing) and not any(
            e["risk"] == "low-medium" for e in actual
        ):
            return (
                'a low-medium patient is missing. Leave out only "low": every'
                " other risk belongs on the watch list."
            )
        for want in missing:
            for got in extra:
                if got["bed"] == want["bed"]:
                    return (
                        f"the entry for bed {want['bed']} should be {want!r},"
                        f" got {got!r}. Hint: use news2_total and news2_risk"
                        " on the patient's observations."
                    )
        return (
            f"expected the beds {[e['bed'] for e in expected]},"
            f" got {[e['bed'] for e in actual]}."
        )
    scores = [e["news2"] for e in actual]
    if any(first < second for first, second in zip(scores, scores[1:], strict=False)):
        return f"the NEWS2 scores come in the order {scores}. Hint: {SORT_HINT}"
    return ""


def _describe(patients):
    if not patients:
        return "an empty ward"
    return f"a ward of {len(patients)} patient{'s' if len(patients) > 1 else ''}"


def watch_list(function):
    name = "build_watch_list"
    if is_placeholder(function):
        return waiting(name)
    if not callable(function):
        return report(
            name, [f"expected a function, got {article(type(function).__name__)}."]
        )
    well = [
        _patient(1, "Alex Morgan"),
        _patient(2, "Sam Okafor", respiration_rate=22, pulse=95),
    ]
    medium_then_high = [
        _patient(1, "Alex Morgan", respiration_rate=22, on_oxygen=True, pulse=95),
        _patient(
            2, "Sam Okafor", respiration_rate=26, on_oxygen=True, spo2=93, pulse=95
        ),
    ]
    one_three = [_patient(5, "Leah Khan", consciousness="C")]
    wards = [[], well, medium_then_high, one_three]
    wards.append(_scale1_ward(data.ward(n_patients=20, seed=42)))
    problems = []
    for patients in wards:
        try:
            actual = function(patients)  # called once, so prints appear once
        except Exception as error:  # report any student error in plain English
            problems.append(
                f"for {_describe(patients)}, {name} raised"
                f" {type(error).__name__}: {error}"
            )
            continue
        if is_placeholder(actual):
            return waiting(name)
        if actual is None:
            problems.append(
                f"{name} returned None. Did you forget to `return` the list?"
            )
            break  # every case will fail the same way
        problem = _watch_problem(actual, _expected_watch_list(patients))
        if problem:
            problems.append(f"for {_describe(patients)}, {problem}")
    return report(name, problems)


# --- Problem 6.7 (stretch): SpO2 scale 2 ------------------------------------


def score_spo2_scale2(function):
    target = "On scale 2, 88-92% is the target range and scores 0."
    hints = {
        (90, False): target,
        (83, False): "83% or lower scores 3.",
        (88, True): target,
        (92, True): target,
        (93, False): "On air, 93% or more scores 0 on scale 2.",
        (97, False): "On air, 93% or more scores 0 on scale 2.",
        (93, True): "On oxygen, 93-94% scores 1.",
        (95, True): "On oxygen, 95-96% scores 2.",
        (97, True): "On oxygen, 97% or more scores 3.",
    }
    values = [
        (90, False),
        (83, False),
        (84, False),
        (85, True),
        (86, False),
        (87, True),
        (88, True),
        (92, True),
        (93, False),
        (97, False),
        (93, True),
        (94, True),
        (95, True),
        (96, True),
        (97, True),
    ]
    cases = [
        Case(args, clinical.score_spo2_scale2(*args), hints.get(args, ""))
        for args in values
    ]
    return check_function("score_spo2_scale2", function, cases)


def news2_scores_scale2(function):
    scale2 = [
        {**_observations(spo2=90), "spo2_scale": 2},
        {**_observations(spo2=97, on_oxygen=True), "spo2_scale": 2},
        {**_observations(spo2=86, on_oxygen=True), "spo2_scale": 2},
    ]
    cases = [
        Case(
            (obs,),
            clinical.news2_parameter_scores(obs),
            'When observations["spo2_scale"] is 2, score SpO2 with'
            " score_spo2_scale2(spo2, on_oxygen).",
        )
        for obs in scale2
    ]
    cases += [
        Case(
            (_observations(spo2=93),),
            clinical.news2_parameter_scores(_observations(spo2=93)),
            "With no spo2_scale key the patient is on scale 1:"
            ' use observations.get("spo2_scale", 1).',
        ),
        Case(
            (_scale1(_observations(spo2=93)),),
            clinical.news2_parameter_scores(_observations(spo2=93)),
            "Scale 1 patients still use score_spo2_scale1.",
        ),
    ]
    scored = check_function("news2_scores", function, cases)
    loud = _check_missing("news2_scores", function)
    return scored and loud


guard_checkers(globals())
