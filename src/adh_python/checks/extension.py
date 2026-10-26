# SPDX-FileCopyrightText: 2026 Bradley Segal
# SPDX-License-Identifier: MIT

"""Helpers and checkers for the extension project: a ward early-warning dashboard.

Students specify NEWS2 behaviour as test cases, generate a scoring function with
an AI assistant, then test and judge it. The tools here never depend on any live
AI output, and every expected answer comes from adh_python.clinical.

A test case is a plain dict:

    {
        "name": "Respiration rate 21, a band edge",
        "observations": {...},  # one round of observations, as in data.ward()
        "expected": {"total": 2, "risk": "low"},  # or the text "ValueError"
    }

`run_tests` runs a list of such cases against any scoring function and reports
which pass. Unlike the checkers, it never raises, even when ADH_STRICT=1:
running tests against code with bugs in it is the point of the exercise.
"""

from __future__ import annotations

import copy

from adh_python import clinical
from adh_python.checks._core import (
    CheckResult,
    article,
    check_value,
    guard_checkers,
    is_number,
    is_placeholder,
    report,
    waiting,
)

ERROR = "ValueError"
RISK_BANDS = ("low", "low-medium", "medium", "high")
MAX_FAILURES_SHOWN = 10
SHOW_EVERY_TEST_UP_TO = 12

# A well adult: every parameter scores 0. The course tests change one thing at
# a time from here, so a failure points at one parameter.
WELL_OBSERVATIONS = {
    "respiration_rate": 16,
    "spo2": 97,
    "on_oxygen": False,
    "systolic_bp": 125,
    "pulse": 72,
    "consciousness": "A",
    "temperature": 36.8,
    "spo2_scale": 1,
}


# --- Tonight's admissions ----------------------------------------------------

# The patients the lesson depends on are built here, explicitly, rather than
# found in data.ward(), so retuning the synthetic ward cannot change the lesson.
# Expected scores (all computed with adh_python.clinical):
#   Margaret Ellis  newly confused, total 7, high. The unfixed draft says 4, low.
#   Arjun Mehta     total 7, high. With no respiration rate, Attempt A says 4, low.
#   Graham Price    SpO2 scale 2, total 5, medium. On scale 1 it would be 8.
# Attempt A calls both totals of 7 medium.
_NEW_ADMISSIONS = [
    {
        "name": "Margaret Ellis",
        "age": 84,
        "diagnosis": "Urinary tract infection",
        "observations": {
            "respiration_rate": 22,
            "spo2": 96,
            "on_oxygen": False,
            "systolic_bp": 118,
            "pulse": 95,
            "consciousness": "C",
            "temperature": 38.4,
            "spo2_scale": 1,
        },
    },
    {
        "name": "Arjun Mehta",
        "age": 67,
        "diagnosis": "Community-acquired pneumonia",
        "observations": {
            "respiration_rate": 25,
            "spo2": 93,
            "on_oxygen": False,
            "systolic_bp": 112,
            "pulse": 116,
            "consciousness": "A",
            "temperature": 37.6,
            "spo2_scale": 1,
        },
    },
    {
        "name": "Graham Price",
        "age": 71,
        "diagnosis": "Exacerbation of COPD",
        "observations": {
            "respiration_rate": 23,
            "spo2": 90,
            "on_oxygen": True,
            "systolic_bp": 134,
            "pulse": 98,
            "consciousness": "A",
            "temperature": 37.2,
            "spo2_scale": 2,
        },
    },
]


def new_admissions(first_bed):
    """Three patients admitted from the emergency department tonight.

    A fresh copy each time, with beds numbered from `first_bed`, so they can
    be added to any ward.
    """
    admissions = copy.deepcopy(_NEW_ADMISSIONS)
    for bed, patient in enumerate(admissions, start=first_bed):
        patient["bed"] = bed
    return admissions


# --- The reference ---------------------------------------------------------


def reference_news2(observations):
    """The course's reference answer, built on adh_python.clinical."""
    return {
        "total": clinical.news2_total(observations),
        "risk": clinical.news2_risk(observations),
    }


def _reference_outcome(observations):
    """The reference total and band, or ERROR if NEWS2 cannot be scored."""
    try:
        return reference_news2(observations)
    except ValueError:
        return ERROR


# --- Band edges, found from clinical rather than restated ------------------

_NUMERIC_SCORERS = {
    "respiration_rate": clinical.score_respiration_rate,
    "systolic_bp": clinical.score_systolic_bp,
    "pulse": clinical.score_pulse,
    "temperature": clinical.score_temperature,
}
_BANDED = ("respiration_rate", "spo2", "systolic_bp", "pulse", "temperature")
_STEP = {"temperature": 0.1}  # recorded to one decimal place; others are whole


def _scorer_for(name, observations):
    """The single-parameter scorer for `name`, or None if it is not numeric."""
    if name == "spo2":
        if observations.get("spo2_scale", 1) == 2:
            on_oxygen = bool(observations.get("on_oxygen"))
            return lambda value: clinical.score_spo2_scale2(value, on_oxygen)
        return clinical.score_spo2_scale1
    return _NUMERIC_SCORERS.get(name)


def _band_edges_in(observations):
    """Names of the parameters whose value sits on the edge of a NEWS2 band."""
    edges = []
    for name in _BANDED:
        value = observations.get(name)
        scorer = _scorer_for(name, observations)
        if scorer is None or not is_number(value):
            continue
        step = _STEP.get(name, 1)
        below = round(value - step, 1)
        above = round(value + step, 1)
        if scorer(below) != scorer(value) or scorer(above) != scorer(value):
            edges.append(name)
    return edges


def _sweep(name):
    """Plausible values of one parameter, lowest first."""
    if name == "temperature":
        return [round(32 + tenth / 10, 1) for tenth in range(101)]
    low, high = {
        "respiration_rate": (0, 60),
        "spo2": (70, 100),
        "systolic_bp": (50, 260),
        "pulse": (20, 200),
    }[name]
    return list(range(low, high + 1))


def _edge_values(name, observations):
    """Every value either side of a change in score, found by sweeping."""
    scorer = _scorer_for(name, observations)
    values = _sweep(name)
    edges = []
    for before, after in zip(values[:-1], values[1:], strict=True):
        if scorer(before) != scorer(after):
            edges += [before, after]
    return edges


def _value_scoring(name, score):
    """The value of `name` nearest the well value that scores `score` alone."""
    scorer = _scorer_for(name, WELL_OBSERVATIONS)
    well = WELL_OBSERVATIONS[name]
    for value in sorted(_sweep(name), key=lambda v: abs(v - well)):
        if scorer(value) == score:
            return value
    raise ValueError(f"no value of {name} scores {score}")


# --- The course test suite --------------------------------------------------

LABELS = {
    "respiration_rate": "Respiration rate",
    "spo2": "SpO2",
    "on_oxygen": "Oxygen",
    "systolic_bp": "Systolic BP",
    "pulse": "Pulse",
    "consciousness": "Consciousness",
    "temperature": "Temperature",
}


def _case(name, observations):
    return {
        "name": name,
        "observations": observations,
        "expected": _reference_outcome(observations),
    }


def _changed(**changes):
    return {**WELL_OBSERVATIONS, **changes}


# Combinations of single-parameter scores that land each side of a risk band.
_RISK_EDGE_COMBINATIONS = [
    {"respiration_rate": 2, "temperature": 1},
    {"respiration_rate": 2, "pulse": 2},
    {"respiration_rate": 2, "pulse": 2, "temperature": 1},
    {"respiration_rate": 2, "pulse": 2, "systolic_bp": 2},
    {"respiration_rate": 2, "pulse": 2, "systolic_bp": 2, "temperature": 1},
    {"respiration_rate": 3, "pulse": 2, "spo2": 2},
]


def course_tests():
    """A systematic test suite: every band edge, both SpO2 scales, every ACVPU
    level, each observation missing in turn, and totals either side of each
    risk band. Expected answers come from adh_python.clinical."""
    tests = []
    for name in _BANDED:
        for value in _edge_values(name, WELL_OBSERVATIONS):
            tests.append(
                _case(f"{LABELS[name]} {value}, a band edge", _changed(**{name: value}))
            )
    for on_oxygen in (True, False):
        base = _changed(spo2_scale=2, on_oxygen=on_oxygen)
        where = "on oxygen" if on_oxygen else "on air"
        for value in _edge_values("spo2", base):
            tests.append(
                _case(f"SpO2 {value} on scale 2, {where}", {**base, "spo2": value})
            )
    tests.append(_case("On oxygen, scale 1", _changed(on_oxygen=True)))
    for level in clinical.ACVPU:
        tests.append(_case(f"Consciousness {level}", _changed(consciousness=level)))
    for combination in _RISK_EDGE_COMBINATIONS:
        values = {name: _value_scoring(name, s) for name, s in combination.items()}
        observations = _changed(**values)
        total = clinical.news2_total(observations)
        described = ", ".join(
            f"{LABELS[name]} {value}" for name, value in values.items()
        )
        tests.append(_case(f"Total {total} ({described})", observations))
    for name in clinical.NEWS2_FIELDS:
        tests.append(
            _case(f"{LABELS[name]} not recorded (None)", _changed(**{name: None}))
        )
    absent = dict(WELL_OBSERVATIONS)
    del absent["pulse"]
    tests.append(_case("Pulse left out of the dict entirely", absent))
    return tests


# --- Running tests against any implementation ------------------------------


def _structure_problem(test):
    """Why a test case is not in the expected shape, or None."""
    if not isinstance(test, dict):
        return f"each test should be a dict, but one is a {type(test).__name__}."
    for key in ("name", "observations", "expected"):
        if key not in test:
            return f"test {test.get('name', '(no name)')!r} has no {key!r} key."
    if not isinstance(test["observations"], dict):
        return f"test {test['name']!r}: 'observations' should be a dict."
    expected = test["expected"]
    if is_placeholder(expected):
        return f"test {test['name']!r} still has ... as its expected answer."
    if expected == ERROR:
        return None
    if not isinstance(expected, dict) or set(expected) != {"total", "risk"}:
        return (
            f"test {test['name']!r}: 'expected' should be a dict like"
            ' {"total": 3, "risk": "low-medium"}, or the text "ValueError".'
        )
    return None


def _describe(outcome):
    if outcome == ERROR:
        return "a ValueError"
    if isinstance(outcome, dict) and set(outcome) >= {"total", "risk"}:
        return f"total {outcome['total']}, risk {outcome['risk']}"
    return repr(outcome)


def _passed(expected):
    if expected == ERROR:
        return "refused with a ValueError, as it should"
    return _describe(expected)


# Plain-English names an error message may use instead of the key itself.
def _unnamed_missing(observations, error):
    """Why a refusal does not name the missing observation, or None if it does."""
    missing = [name for name in clinical.NEWS2_FIELDS if observations.get(name) is None]
    message = str(error).lower()
    if not missing or any(clinical.names_observation(message, f) for f in missing):
        return None
    return (
        f"it refused with ValueError: {error}, but the message does not say which"
        f" observation is missing ({', '.join(missing)}). The nurse needs to know"
        " what to re-measure, so put its name in the message, for example"
        f' ValueError("{missing[0]} is missing").'
    )


def _failure(test, function):
    """A plain-English reason this test fails, or None if it passes."""
    expected = test["expected"]
    try:
        actual = function(copy.deepcopy(test["observations"]))
    except ValueError as error:
        if expected == ERROR:
            return _unnamed_missing(test["observations"], error)
        return f"expected {_describe(expected)}, but it raised ValueError: {error}"
    except Exception as error:  # report any error in the code under test
        if expected == ERROR:
            return (
                f"it stopped, but with {type(error).__name__}: {error}."
                " The requirement is a ValueError that names the missing observation."
            )
        return (
            f"expected {_describe(expected)}, but it raised"
            f" {type(error).__name__}: {error}"
        )
    if expected == ERROR:
        return (
            f"expected a ValueError, but it returned {_describe(actual)}."
            " It scored a patient with a missing observation instead of refusing."
        )
    if isinstance(actual, (tuple, list)) and len(actual) == 2:
        return (
            f"it returned {actual!r}, but the tests expect a dict such as"
            f" {{'total': {expected['total']}, 'risk': {expected['risk']!r}}}."
        )
    if not isinstance(actual, dict) or not {"total", "risk"} <= set(actual):
        return f"it returned {actual!r}; expected a dict with 'total' and 'risk'."
    if actual["total"] != expected["total"] or actual["risk"] != expected["risk"]:
        return f"expected {_describe(expected)}, got {_describe(actual)}."
    return None


def run_tests(tests, score_function):
    """Run each test case against `score_function` and report which pass.

    Returns a CheckResult, truthy if every test passes. Never raises, so a notebook keeps
    running when the code under test is wrong.
    """
    if is_placeholder(tests) or is_placeholder(score_function):
        print("⏳ Nothing to test yet. Replace the ... above, then run this cell.")
        return CheckResult(False)
    if not callable(score_function):
        print(
            f"❌ Expected a function to test, got {article(type(score_function).__name__)}."
        )
        return CheckResult(False)
    if not isinstance(tests, list) or not tests:
        print("❌ Expected a list of test cases with at least one test in it.")
        return CheckResult(False)
    for test in tests:
        problem = _structure_problem(test)
        if problem:
            print(f"❌ Cannot run the tests: {problem}")
            return CheckResult(False)

    label = getattr(score_function, "__name__", "your function")
    print(f"Running {len(tests)} tests on {label}:")
    show_every_test = len(tests) <= SHOW_EVERY_TEST_UP_TO
    failures = 0
    for test in tests:
        reason = _failure(test, score_function)
        if reason is None:
            if show_every_test:
                print(f"✅ {test['name']}: {_passed(test['expected'])}.")
            continue
        failures += 1
        if failures <= MAX_FAILURES_SHOWN:
            print(f"❌ {test['name']}: {reason}")
    if failures > MAX_FAILURES_SHOWN:
        print(f"   …and {failures - MAX_FAILURES_SHOWN} more failures.")
    passed = len(tests) - failures
    print(f"{passed} of {len(tests)} tests passed.")
    return CheckResult(failures == 0)


# --- The dashboard ----------------------------------------------------------


def ward_dashboard(patients, score_function):
    """Print the ward, sickest first, using any scoring function.

    A patient the function cannot score is listed first, so a gap in the
    observations is seen rather than hidden.
    """
    if is_placeholder(score_function):
        print("⏳ No scoring function yet. Replace the ... above, then run this cell.")
        return
    unscored, scored = [], []
    for patient in patients:
        try:
            result = score_function(copy.deepcopy(patient["observations"]))
            total, risk = result["total"], result["risk"]
        except Exception as error:  # show any failure on the board, not a crash
            unscored.append((patient, f"{type(error).__name__}: {error}"))
            continue
        scored.append((total, patient, risk))

    print(f"{'Bed':>3}  {'Name':<18} {'NEWS2':>5}  Risk")
    for patient, message in unscored:
        print(
            f"{patient['bed']:>3}  {patient['name']:<18} {'?':>5}  CANNOT SCORE ({message})"
        )
    scored.sort(key=lambda row: (-row[0], row[1]["bed"]))
    for total, patient, risk in scored:
        shown = risk.upper() if risk == "high" else risk
        print(f"{patient['bed']:>3}  {patient['name']:<18} {total:>5}  {shown}")


# --- Checkers ---------------------------------------------------------------


def _check_topics(name, text, topics, hint):
    if is_placeholder(text):
        return waiting(name)
    if not isinstance(text, str):
        return report(
            name, [f"expected text (a str), got {article(type(text).__name__)}."]
        )
    lowered = text.lower()
    missing = [label for label, words in topics if not any(w in lowered for w in words)]
    if not missing:
        return report(name, [], success="recorded")
    return report(
        name, [f"I could not find anything about {label}. {hint}" for label in missing]
    )


# Ordinary ways of saying an observation is missing, and that the code refuses.
_MISSING_WORDS = [
    "missing",
    "not recorded",
    "unrecorded",
    "not measured",
    "not taken",
    "absent",
    "blank",
    "empty",
    "null",
    "none",
    "incomplete",
    "not available",
    "unavailable",
    "not present",
    "left out",
    "gap",
]
_REFUSAL_WORDS = [
    "error",
    "exception",
    "raise",
    "refuse",
    "reject",
    "stop",
    "halt",
    "warn",
    "fail",
    "flag",
    "decline",
    "do not score",
    "don't score",
    "not score",
    "cannot score",
]
_ADVISORY = (
    "The checker only looks for key words, so treat this as a checklist:"
    " if you covered it in other words, move on."
)

_REQUIREMENT_TOPICS = [
    (
        "what goes in (the observations)",
        ["observation", "vital", "obs", "input", "measurement"],
    ),
    ("the NEWS2 total", ["total", "score", "sum"]),
    ("the risk band", ["risk", "band"]),
    ("missing observations", _MISSING_WORDS),
    ("SpO2 scale 2", ["scale 2", "scale two", "hypercapni", "88"]),
    ("new confusion", ["confus", "acvpu"]),
    ("what happens when it cannot score", _REFUSAL_WORDS),
]


def requirements(text):
    """Plain-English requirements should cover the awkward cases, not just the
    happy path."""
    return _check_topics("Requirements", text, _REQUIREMENT_TOPICS, _ADVISORY)


_PROMPT_TOPICS = [
    ("the function name score_news2", ["score_news2"]),
    ("the input data structure (paste an example dict)", ["respiration_rate"]),
    ("what it should return (the total and the risk band)", ["total", "sum"]),
    ("the risk band labels", ["low-medium", "low medium"]),
    ("what to do when an observation is missing", _MISSING_WORDS),
    ("SpO2 scale 2", ["scale 2", "scale two", "spo2_scale", "hypercapni", "88-92"]),
    ("asking for test cases", ["test"]),
    (
        "asking it to explain the code",
        ["explain", "explanation", "walk me through", "talk me through"],
    ),
]


def prompt(text):
    """A good prompt states inputs and outputs, gives the data, and asks for
    tests and an explanation."""
    return _check_topics(
        "Prompt",
        text,
        _PROMPT_TOPICS,
        f"Look at the prompt card above for what a good request includes. {_ADVISORY}",
    )


def _parameter_breakdown(observations):
    try:
        scores = clinical.news2_parameter_scores(observations)
    except (ValueError, TypeError):
        return ""
    shown = ", ".join(f"{name} {score}" for name, score in scores.items())
    return f" The RCP chart scores each parameter as: {shown}."


def _case_problem(test):
    """Why one test case's expectation disagrees with the RCP chart, or None."""
    observations = test["observations"]
    level = observations.get("consciousness")
    if level is not None and level not in clinical.ACVPU:
        return (
            f"{test['name']!r}: consciousness is {level!r}. Use one of the letters"
            f" {', '.join(clinical.ACVPU)}, as the ward data does."
        )
    if observations.get("spo2_scale", 1) not in (1, 2):
        return f"{test['name']!r}: spo2_scale should be 1 or 2."
    try:
        truth = _reference_outcome(observations)
    except Exception as error:  # say why the reference could not score it
        return (
            f"{test['name']!r}: the reference could not score these observations"
            f" ({type(error).__name__}: {error}). Are the values numbers?"
        )
    expected = test["expected"]
    if expected == truth:
        return None
    problem = (
        f"{test['name']!r}: you expect {_describe(expected)},"
        f" the RCP chart gives {_describe(truth)}."
    )
    if truth == ERROR:
        return problem + (
            " A missing observation cannot be scored as if it were normal;"
            ' expect the code to refuse with "ValueError".'
        )
    if expected == ERROR:
        return problem + " Every observation is present, so this case can be scored."
    if expected["risk"] not in RISK_BANDS:
        return problem + (
            f" Risk bands are written exactly as {', '.join(map(repr, RISK_BANDS))}."
        )
    if expected["total"] == truth["total"]:
        return problem + (
            " The total is right; check how the chart turns it into a risk band,"
            " including the rule for a single parameter scoring 3."
        )
    return problem + _parameter_breakdown(observations)


_COVERAGE = [
    ("missing", "a missing observation the code should refuse"),
    ("edge", "a value exactly on the edge of a NEWS2 band"),
    ("scale2", "a patient on SpO2 scale 2"),
    ("confused", "a newly confused patient (consciousness 'C')"),
]


def _kinds_covered(tests):
    kinds = set()
    for test in tests:
        observations = test["observations"]
        if test["expected"] == ERROR:
            kinds.add("missing")
            continue
        if _band_edges_in(observations):
            kinds.add("edge")
        if observations.get("spo2_scale") == 2:
            kinds.add("scale2")
        if observations.get("consciousness") == "C":
            kinds.add("confused")
    return kinds


def test_cases(tests):
    """Every expectation must agree with the RCP chart, and the list must include
    the awkward cases."""
    name = "Test cases"
    if is_placeholder(tests):
        return waiting(name)
    if not isinstance(tests, list) or not tests:
        return report(name, ["expected a list of test cases (dicts)."])
    for test in tests:
        problem = _structure_problem(test)
        if problem:
            return report(name, [problem])
    case_problems = [_case_problem(test) for test in tests]
    problems = [p for p in case_problems if p]
    covered = _kinds_covered(
        [t for t, p in zip(tests, case_problems, strict=True) if not p]
    )
    for kind, label in _COVERAGE:
        if kind not in covered:
            problems.append(f"no test yet for {label}.")
    return report(name, problems)


def fixed_draft(score_function):
    """After the fix, the draft must pass the whole course suite."""
    name = "Fixed draft"
    if is_placeholder(score_function):
        return waiting(name)
    problems = []
    for test in course_tests():
        reason = _failure(test, score_function)
        if reason is None:
            continue
        problem = f"{test['name']}: {reason}"
        if test["observations"].get("consciousness") == "C":
            problem += (
                " Hint: NEWS2 scores new confusion (C) like V, P and U. The draft"
                " follows the older NEWS chart, which had no C. The course's"
                " clinical.score_consciousness already gets this right."
            )
        problems.append(problem)
    return report(name, problems)


def predict_missing_value(score_function, observations, prediction):
    """Predict what Attempt A reports for a patient with a missing observation."""
    if is_placeholder(prediction):
        return waiting("Prediction")
    try:
        actual = score_function(copy.deepcopy(observations))["total"]
    except ValueError:
        actual = ERROR
    except Exception as error:  # the attempt itself was changed or broken
        return report(
            "Prediction", [f"the attempt raised {type(error).__name__}: {error}."]
        )
    if prediction == ERROR and actual != ERROR:
        hint = (
            "Attempt A never stops for a missing value: `if obs.get(name) is "
            "not None` silently skips it and sums everything else."
        )
    else:
        hint = "Score each parameter that is present; the missing one adds nothing."
    return check_value("Prediction", prediction, actual, hint=hint)


def shows_wrong_answer(score_function, observations):
    """A complete set of observations on which the function disagrees with the
    RCP chart."""
    name = "Wrong-answer example"
    if is_placeholder(observations):
        return waiting(name)
    if not isinstance(observations, dict):
        return report(name, [f"expected a dict of observations, got {observations!r}."])
    truth = _reference_outcome(observations)
    if truth == ERROR:
        return report(
            name,
            [
                "these observations have something missing. You have already shown"
                " that bug; find a complete set where Attempt A gives the wrong answer."
            ],
        )
    try:
        actual = score_function(copy.deepcopy(observations))
    except Exception as error:  # a crash is not a wrong answer
        return report(name, [f"it raised {type(error).__name__}: {error}."])
    if actual == truth:
        return report(
            name,
            [
                f"Attempt A gets this one right ({_describe(truth)}). Hint: look at"
                " the course tests it failed that are not about missing values,"
                " or compare Margaret Ellis and Arjun Mehta on the two dashboards."
            ],
        )
    print(f"Attempt A says {_describe(actual)}; the RCP chart says {_describe(truth)}.")
    return report(name, [])


MIN_REASON_WORDS = 8

# What a reason can draw on, from the tests and the trade-offs section.
_EVIDENCE = [
    ("the tests", ["test", "suite", "pass", "fail"]),
    (
        "failing loudly or silently",
        _MISSING_WORDS + ["refus", "loud", "silent", "quiet", "error", "raise"],
    ),
    (
        "readability",
        [
            "readab",
            "to read",
            "clear",
            "understand",
            "check",
            "simple",
            "short",
            "long",
            "compact",
        ],
    ),
    (
        "maintenance",
        ["maintain", "maintenance", "inherit", "owner", "change", "revis", "threshold"],
    ),
]

# What must change before Attempt A could go further, and words that show a
# reason already names it.
_A_FIXES = [
    (
        ["missing", "none", "absent", "incomplete", "skip", "refus", "silent"],
        "it scores a missing observation as normal (`if obs.get(name) is not None`"
        " skips it, and a missing oxygen or consciousness is read as air or alert)."
        " It must raise a ValueError that names what is missing.",
    ),
    (
        ["7", ">", "boundary", "threshold", "edge"],
        "`total > 7` calls a total of exactly 7 medium; the chart puts 7 in the"
        " high band, so it must be `total >= 7`.",
    ),
]


def build_on(choice, reason):
    """Which attempt to take forward, and why. Either can be defended, so the
    choice is recorded, not marked; the reason must draw on the evidence."""
    name = "Your decision"
    if is_placeholder(choice) or is_placeholder(reason):
        return waiting(name)
    problems = []
    letter = str(choice).strip().upper()
    if letter not in ("A", "B"):
        problems.append('write "A" or "B" for the attempt you would build on.')
    words = reason.lower() if isinstance(reason, str) else ""
    drawn_on = [label for label, keys in _EVIDENCE if any(k in words for k in keys)]
    if len(words.split()) < MIN_REASON_WORDS:
        problems.append(
            f"give your reasons in a sentence or two (at least {MIN_REASON_WORDS}"
            " words): what did the tests show, and what would you still change?"
        )
    elif not drawn_on:
        problems.append(
            "say what your choice rests on: what the tests showed, how each"
            " attempt handled a missing observation, how easily it can be checked"
            " against the chart, or who would maintain it."
        )
    if problems:
        return report(name, problems)
    result = report(name, [], success="recorded")
    print(f"   Your reason draws on {', '.join(drawn_on)}.")
    if letter == "A":
        unnamed = [fix for keys, fix in _A_FIXES if not any(k in words for k in keys)]
        if unnamed:
            print(
                "   Before building on A, fix these first, then re-run the course suite:"
            )
            for fix in unnamed:
                print(f"   • {fix}")
        else:
            print(
                "   You named both bugs A must lose first. Fix one at a time and"
                " re-run the course suite after each."
            )
    elif not any(k in words for k in ("threshold", "owner", "clinical", "copied")):
        print(
            "   B passed the tests, but it restates every threshold of the chart."
            " What would you change before using it? For example, call the tested"
            " functions in clinical, as the draft did."
        )
    return result


guard_checkers(globals(), skip=("new_admissions", "reference_news2", "course_tests"))
