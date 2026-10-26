# SPDX-FileCopyrightText: 2026 Bradley Segal
# SPDX-License-Identifier: MIT

"""Checkers for Level 3: booleans, comparisons and decisions.

Most problems here give the student a small function to fill in, so the
checker can try their if-block on many values, including every boundary.
Expected answers come from adh_python.clinical, never from a copy of it.
"""

from __future__ import annotations

from adh_python import clinical
from adh_python.checks._core import (
    Case,
    check_function,
    check_value,
    guard_checkers,
    is_placeholder,
    report,
)


def predict_branch(prediction):
    rate = 21
    hints = {
        0: f"{rate} <= 20 is False, so that branch is skipped and Python tries the next elif.",
        1: f"{rate} <= 11 is False, so that branch is skipped.",
        3: f"Python stops at the first condition that is True. {rate} <= 24 is True, so else never runs.",
    }
    hint = "Work down the conditions; only the first True one runs."
    if type(prediction) is int:  # a list, say, cannot be looked up in hints
        hint = hints.get(prediction, hint)
    return check_value(
        "Prediction", prediction, clinical.score_respiration_rate(rate), hint=hint
    )


def bmi_category(function):
    def case(value, hint=""):
        return Case((value,), clinical.bmi_category(value), hint)

    def edge(value):
        return case(
            value,
            f"A BMI of exactly {value} is {clinical.bmi_category(value)}: a value on"
            " a boundary belongs to the band above. Check < versus <=.",
        )

    return check_function(
        "bmi_category",
        function,
        [
            case(22.0),
            case(17.0),
            edge(18.5),
            case(24.9),
            edge(25.0),
            case(29.9),
            case(41.0, "The highest band is missing. Did you add an elif for it?"),
            edge(30.0),
        ],
    )


def score_temperature(function):
    def top_of_band(value):
        return Case(
            (value,),
            clinical.score_temperature(value),
            f"{value} scores {clinical.score_temperature(value)}: each band on the"
            " chart includes its top value. Use <= rather than <.",
        )

    def start_of_band(value):
        return Case(
            (value,),
            clinical.score_temperature(value),
            f"{value} scores {clinical.score_temperature(value)}: it is the first"
            " value of the next band up.",
        )

    return check_function(
        "score_temperature",
        function,
        [
            Case((37.0,), clinical.score_temperature(37.0)),
            Case((34.2,), clinical.score_temperature(34.2)),
            top_of_band(35.0),
            start_of_band(35.1),
            top_of_band(36.0),
            start_of_band(36.1),
            top_of_band(38.0),
            start_of_band(38.1),
            top_of_band(39.0),
            start_of_band(39.1),
            Case(
                (40.3,), clinical.score_temperature(40.3), "Is the else branch there?"
            ),
        ],
    )


def has_red_score(function):
    separate = (
        "No parameter scores 3 here. Each side of or needs its own comparison:"
        " respiration_score == 3 or spo2_score == 3 or pulse_score == 3."
        " Writing respiration_score or spo2_score or pulse_score == 3 does not"
        " compare the first two with 3."
    )
    cases = [
        Case((0, 0, 0), False),
        Case((3, 0, 0), True, "One parameter scoring 3 is enough. Use or, not and."),
        Case((0, 3, 0), True, "Is spo2_score part of your condition?"),
        Case((0, 0, 3), True, "Is pulse_score part of your condition?"),
        Case((1, 2, 1), False, separate),
        Case((2, 2, 2), False),
        Case((3, 3, 3), True),
    ]
    return _true_or_false_rule(
        "has_red_score",
        function,
        cases,
        "Each side of or needs its own == 3:"
        " respiration_score == 3 or spo2_score == 3 or pulse_score == 3.",
    )


def both_scoring(function):
    return _true_or_false_rule(
        "both_scoring",
        function,
        [
            Case((1, 1), True),
            Case((0, 0), False),
            Case((1, 0), False, "Both must be scoring. Use and, not or."),
            Case(
                (0, 2),
                False,
                "Both must be scoring. Give each side of and its own comparison:"
                " temperature_score > 0 and pulse_score > 0.",
            ),
            Case(
                (2, 3), True, "Any score above 0 counts, not only 1. Compare with > 0."
            ),
            Case((3, 1), True),
        ],
        "Each side of and needs its own comparison:"
        " temperature_score > 0 and pulse_score > 0.",
    )


def score_spo2(function):
    def case(value, hint=""):
        return Case((value,), clinical.score_spo2_scale1(value), hint)

    return check_function(
        "score_spo2",
        function,
        [
            case(97),
            case(96),
            case(95),
            case(94),
            case(
                93,
                "Python stops at the first condition that is True. If spo2 <= 95"
                " is checked first, it catches every low reading, so the branches"
                " below it never run. Put the lowest band first.",
            ),
            case(92),
            case(91, "Is the lowest band checked first?"),
            case(86),
        ],
    )


def _true_or_false_rule(name, function, cases, fix):
    """Check a rule that must give True or False.

    A condition such as `a or b or c == 3` gives back a score, not True or
    False. Name that before any case-specific hint, which would otherwise
    blame the wrong part of the condition. Each case calls the student's
    function only once.
    """
    if not callable(function):
        return check_function(name, function, cases)
    answers = {}
    for case in cases:
        try:
            answer = function(*case.args)
        except Exception as error:  # check_function reports it in plain English
            answers[case.args] = error
            break
        answers[case.args] = answer
        if answer is None or is_placeholder(answer):
            break
        if not isinstance(answer, bool):
            return report(
                name,
                [f"{name}{case.args} returned {answer!r}, not {case.expected}. {fix}"],
            )

    def answer_once(*args):
        if args not in answers:
            return function(*args)
        if isinstance(answers[args], Exception):
            raise answers[args]
        return answers[args]

    return check_function(name, answer_once, cases)


guard_checkers(globals())
