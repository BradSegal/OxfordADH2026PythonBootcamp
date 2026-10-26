# SPDX-FileCopyrightText: 2026 Bradley Segal
# SPDX-License-Identifier: MIT

"""Plain-English feedback for practice problems.

Every checker prints feedback and returns a CheckResult, which is truthy when
the answer is right but is not echoed under the feedback in a notebook. A
checker never raises in a student notebook, so a notebook can always be run from top to bottom. When the
environment variable ADH_STRICT=1 is set (as it is when the solution notebooks
are run automatically to test the course), a failed check raises
AssertionError instead.
"""

from __future__ import annotations

import functools
import inspect
import math
import numbers
import os
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

MAX_PROBLEMS_SHOWN = 3


@dataclass(frozen=True)
class Case:
    """One input and the answer we expect for it.

    `hint` is shown when this case fails. Use it to name the likely mistake,
    for example "Is 25.0 overweight? Check < versus <=."
    """

    args: tuple
    expected: Any
    hint: str = ""


class CheckResult:
    """Pass or fail, without a stray True/False printed under the feedback.

    Behaves like a bool in `if`, `assert` and `==`. The printed feedback is the
    output students should read, so `_ipython_display_` shows nothing more.
    """

    __slots__ = ("passed",)

    def __init__(self, passed: bool) -> None:
        self.passed = passed

    def __bool__(self) -> bool:
        return self.passed

    def __eq__(self, other: object) -> bool:
        if isinstance(other, (bool, CheckResult)):
            return self.passed == bool(other)
        return NotImplemented

    def __hash__(self) -> int:
        return hash(self.passed)

    def __repr__(self) -> str:
        return repr(self.passed)

    def _ipython_display_(self) -> None:
        pass


def _strict() -> bool:
    return os.environ.get("ADH_STRICT") == "1"


# Building blocks for level-specific checkers (for example array checks in
# Level 7): `is_placeholder` spots an untouched `...`, `waiting` reports it,
# `report` prints the verdict for a list of problems (empty means correct), and
# `is_number` and `near` test a student's number while choosing a hint.


def is_placeholder(value: Any) -> bool:
    return value is Ellipsis


def is_number(value: Any) -> bool:
    """True for a single real number, numpy ones included, but not True or False."""
    return isinstance(value, numbers.Real) and not isinstance(value, bool)


def near(actual: Any, expected: float, tolerance: float = 1e-6) -> bool:
    """True when `actual` is a single number within `tolerance` of `expected`."""
    if not is_number(actual):
        return False
    try:
        return abs(float(actual) - float(expected)) <= tolerance
    except OverflowError:  # an int too large to be a float
        return False


def _close(actual: Any, expected: Any, tolerance: float) -> bool:
    """Compare a student's answer with the expected one, never raising.

    True and False are not treated as 1 and 0; a list is not a tuple; dicts
    are compared key by key with the same rules; numbers within `tolerance`
    count as equal.
    """
    if isinstance(expected, bool) or isinstance(actual, bool):
        return actual is expected
    if isinstance(expected, (int, float)) and isinstance(actual, (int, float)):
        try:
            return math.isclose(actual, expected, rel_tol=0, abs_tol=tolerance)
        except (TypeError, OverflowError):
            return False
    if isinstance(expected, (list, tuple)):
        return (
            type(actual) is type(expected)
            and len(actual) == len(expected)
            and all(
                _close(a, e, tolerance) for a, e in zip(actual, expected, strict=True)
            )
        )
    if isinstance(expected, dict):
        return (
            isinstance(actual, dict)
            and actual.keys() == expected.keys()
            and all(_close(actual[k], expected[k], tolerance) for k in expected)
        )
    try:
        return bool(actual == expected)
    except Exception:  # e.g. a numpy array compared with a single value
        return False


def article(noun: str) -> str:
    return f"an {noun}" if noun[:1] in "aeiou" else f"a {noun}"


def _show_args(args: tuple) -> str:
    return ", ".join(repr(a) for a in args)


def report(name: str, problems: list[str], success: str = "correct") -> CheckResult:
    """Print the verdict. `success` lets judgement checks say "recorded" instead."""
    if not problems:
        print(f"✅ {name}: {success}.")
        return CheckResult(True)
    print(f"❌ {name}: not yet.")
    for problem in problems[:MAX_PROBLEMS_SHOWN]:
        print(f"   • {problem}")
    if len(problems) > MAX_PROBLEMS_SHOWN:
        print(f"   • …and {len(problems) - MAX_PROBLEMS_SHOWN} more.")
    if _strict():
        raise AssertionError(f"{name}: " + " | ".join(problems))
    return CheckResult(False)


def waiting(name: str) -> CheckResult:
    print(f"⏳ {name}: not attempted yet. Replace the ... above, then run this cell.")
    if _strict():
        raise AssertionError(f"{name}: not attempted")
    return CheckResult(False)


def check_value(
    name: str,
    actual: Any,
    expected: Any,
    hint: str = "",
    tolerance: float = 0.01,
    exact_type: bool = False,
) -> CheckResult:
    """Check a value the student computed, such as a variable.

    With `exact_type=True` the answer must also have the expected type, for
    problems that teach a conversion (for example 128 rather than 128.0).
    """
    if is_placeholder(actual):
        return waiting(name)
    right_type = type(actual) is type(expected) or not exact_type
    if right_type and _close(actual, expected, tolerance):
        return report(name, [])
    problem = f"expected {expected!r}, got {actual!r}."
    if type(actual) is not type(expected) and (
        exact_type
        or not (isinstance(actual, (int, float)) and isinstance(expected, (int, float)))
    ):
        problem += (
            f" Your answer is {article(type(actual).__name__)},"
            f" but {article(type(expected).__name__)} was expected."
        )
    if hint:
        problem += f" Hint: {hint}"
    return report(name, [problem])


def check_function(
    name: str,
    function: Callable[..., Any],
    cases: list[Case],
    tolerance: float = 0.01,
) -> CheckResult:
    """Call the student's function on each case and compare the answers."""
    if is_placeholder(function):
        return waiting(name)
    if not callable(function):
        return report(
            name, [f"expected a function, got {article(type(function).__name__)}."]
        )
    problems = []
    for case in cases:
        try:
            actual = function(*case.args)
        except Exception as error:  # report any student error in plain English
            problems.append(
                f"{name}({_show_args(case.args)}) raised "
                f"{type(error).__name__}: {error}"
            )
            continue
        if is_placeholder(actual):  # the scaffold still returns the ... placeholder
            return waiting(name)
        if actual is None and case.expected is not None:
            problems.append(
                f"{name}({_show_args(case.args)}) returned None."
                " Did you forget to `return` the answer?"
            )
            break  # every case will fail the same way
        if not _close(actual, case.expected, tolerance):
            problem = (
                f"{name}({_show_args(case.args)}) should be "
                f"{case.expected!r}, got {actual!r}."
            )
            if case.hint:
                problem += f" Hint: {case.hint}"
            problems.append(problem)
    return report(name, problems)


def check_output(
    name: str, printed: str, must_contain: list[str], hint: str = ""
) -> CheckResult:
    """Check text the student built, such as a formatted message."""
    if is_placeholder(printed):
        return waiting(name)
    if not isinstance(printed, str):
        return report(
            name, [f"expected text (a str), got {article(type(printed).__name__)}."]
        )
    missing = [part for part in must_contain if part not in printed]
    if not missing:
        return report(name, [])
    problem = "your text is missing: " + ", ".join(repr(m) for m in missing) + "."
    if hint:
        problem += f" Hint: {hint}"
    return report(name, [problem])


def guard_checkers(namespace: dict, skip: tuple[str, ...] = ()) -> None:
    """Make every public checker in a module safe to call with any answer.

    Call once at the end of a checker module: `guard_checkers(globals())`.
    A checker that hits an unexpected error (for example a hint that assumed a
    list and got None) then prints a plain-English message instead of a
    traceback. In strict mode the error is raised, so automated testing still sees it. Names
    in `skip` (such as reference implementations students test against, which
    must raise ValueError) are left untouched.
    """
    module = namespace["__name__"]
    for name, value in list(namespace.items()):
        if (
            inspect.isfunction(value)
            and value.__module__ == module
            and not name.startswith("_")
            and name not in skip
        ):
            namespace[name] = _guarded(value)


def _guarded(checker: Callable[..., Any]) -> Callable[..., Any]:
    @functools.wraps(checker)
    def guarded(*args: Any, **kwargs: Any) -> Any:
        try:
            return checker(*args, **kwargs)
        except Exception as error:
            if _strict():
                raise
            label = checker.__name__.replace("_", " ").capitalize()
            print(
                f"❌ {label}: the checker could not read this answer"
                f" ({type(error).__name__}: {error}). Check that it is the kind"
                " of value the problem asks for, then run the cell again."
            )
            return CheckResult(False)

    guarded.adh_checker = True  # lets tests find every checker
    return guarded
