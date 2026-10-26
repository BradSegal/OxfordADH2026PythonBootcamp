# SPDX-FileCopyrightText: 2026 Bradley Segal
# SPDX-License-Identifier: MIT

"""Checkers for Level 7: libraries, arrays and images.

Each checker takes the inputs the student used as well as their answer. Arrays
are checked for shape before values, because a wrong shape is the commonest
mistake and the most useful one to name. Every hint names a specific
misconception: row and column order, slice ends, uint8 overflow, or forgetting
to divide by 255.
"""

from __future__ import annotations

import numpy as np

from adh_python.checks._core import (
    guard_checkers,
    is_placeholder,
    near,
    report,
    waiting,
)

# The zones used in the notebook, as (first row, end row, first column, end column).
# The left box sits just lateral to the heart border, so both are lung.
RIGHT_LOWER_ZONE = (450, 550, 180, 260)
LEFT_LOWER_ZONE = (450, 550, 790, 870)
PREDICT_SLICE_SHAPE = (200, 400)  # xray[100:300, 50:450]
UINT8_MAX = 255


def _number(value) -> float:
    """`value` as a float, or NaN (which is never near anything) if it is not one."""
    try:
        return float(value)
    except (TypeError, ValueError, OverflowError):
        return float("nan")


def _whole_number(value):
    """`value` as an int if it is a whole number (not a bool), otherwise None."""
    if isinstance(value, (bool, np.bool_)):
        return None
    if isinstance(value, (int, np.integer)):
        return int(value)
    if isinstance(value, (float, np.floating)) and float(value).is_integer():
        return int(value)
    return None


def _lobar_film():
    from PIL import Image

    from adh_python.imaging.images import image_path

    return np.array(Image.open(image_path("lobar_pneumonia")))


def _crop(image, zone):
    first_row, end_row, first_col, end_col = zone
    return image[first_row:end_row, first_col:end_col]


def _not_an_array(label, value) -> str:
    return (
        f"`{label}` should be a numpy array, but it is a {type(value).__name__}."
        " Slicing an array gives you an array."
    )


def grey_levels(bits, levels, brightest):
    name = "Grey levels"
    if is_placeholder(levels) or is_placeholder(brightest):
        return waiting(name)
    if not isinstance(bits, int) or isinstance(bits, bool) or not 1 <= bits <= 64:
        return report(name, [f"`bits` should be a whole number of bits, got {bits!r}."])
    expected = 2**bits
    problems = []
    if not near(levels, expected):
        problem = f"`levels` should be {expected}, got {levels!r}."
        if near(levels, 2 * bits):
            problem += (
                " Hint: 2 * bits multiplies. Each extra bit doubles the number of"
                " patterns, which is a power: 2 ** bits."
            )
        elif near(levels, bits**2):
            problem += (
                " Hint: bits ** 2 is the wrong way round. Two choices per bit,"
                " multiplied once for every bit, is 2 ** bits."
            )
        else:
            problem += " Hint: each bit doubles the number of patterns: 2 ** bits."
        problems.append(problem)
    # If `levels` is wrong but `brightest` is levels - 1, report only `levels`.
    follows_from_levels = bool(problems) and near(brightest, _number(levels) - 1)
    if not near(brightest, expected - 1) and not follows_from_levels:
        problem = f"`brightest` should be {expected - 1}, got {brightest!r}."
        if near(brightest, expected):
            problem += (
                f" Hint: counting starts at 0 (black), so {expected} levels run"
                f" from 0 to {expected - 1}. The brightest value is levels - 1."
            )
        else:
            problem += " Hint: the darkest value is 0, so the brightest is levels - 1."
        problems.append(problem)
    return report(name, problems)


def predict_crop_shape(prediction):
    name = "Prediction"
    if is_placeholder(prediction):
        return waiting(name)
    rows, cols = PREDICT_SLICE_SHAPE
    if near(prediction, rows * cols):
        return report(
            name,
            [
                f"{prediction!r} is the number of pixels. A shape is two numbers,"
                " (rows, columns). Hint: write it as (rows, columns)."
            ],
        )
    try:
        guess = tuple(_whole_number(n) for n in prediction)
    except TypeError:  # not a collection, such as a single number
        guess = (None,)
    if len(guess) != 2 or None in guess:
        return report(
            name,
            [
                f"expected two whole numbers in brackets like (rows, columns),"
                f" got {prediction!r}. A shape counts rows and columns, so"
                " each number is whole."
            ],
        )
    if guess == PREDICT_SLICE_SHAPE:
        return report(name, [])
    problem = f"expected {PREDICT_SLICE_SHAPE}, got {prediction!r}."
    if guess == (cols, rows):
        problem += (
            " Hint: rows come first. A shape is (height, width), so the row"
            " slice 100:300 gives the first number."
        )
    elif guess == (rows + 1, cols + 1):
        problem += (
            " Hint: the end of a slice is not included. 100:300 is rows 100 to"
            " 299, which is 300 - 100 = 200 rows."
        )
    elif guess == (300, 450):
        problem += (
            " Hint: 300 and 450 are where the slices stop, not their sizes. The"
            " size of a slice is end minus start."
        )
    elif guess == (814, 1024):
        problem += " Hint: slicing keeps only the region you ask for, so it is smaller."
    else:
        problem += (
            " Hint: the size of a slice is end minus start: 300 - 100 rows and"
            " 450 - 50 columns."
        )
    return report(name, [problem])


def left_zone(xray, left_lower):
    name = "Left lower zone"
    if is_placeholder(left_lower):
        return waiting(name)
    if not isinstance(left_lower, np.ndarray):
        return report(name, [_not_an_array("left_lower", left_lower)])
    expected = _crop(xray, LEFT_LOWER_ZONE)
    if left_lower.shape == expected.shape and np.array_equal(left_lower, expected):
        return report(name, [])
    first_row, end_row, first_col, end_col = LEFT_LOWER_ZONE
    if left_lower.shape == expected.shape and np.array_equal(
        left_lower, _crop(xray, RIGHT_LOWER_ZONE)
    ):
        problem = (
            "this is still the right lower zone. Hint: keep the rows and change"
            f" the columns to {first_col}:{end_col}."
        )
    elif np.array_equal(left_lower, xray[first_col:end_col, first_row:end_row]):
        problem = (
            "rows and columns are swapped. Hint: an array is indexed"
            f" [rows, columns], so write xray[{first_row}:{end_row},"
            f" {first_col}:{end_col}]."
        )
    elif left_lower.shape != expected.shape:
        problem = (
            f"the shape should be {expected.shape}, got {left_lower.shape}."
            f" Hint: rows {first_row}:{end_row} and columns {first_col}:{end_col}."
            " The number after the colon is where the slice stops, and that row"
            " or column is not included."
        )
    else:
        problem = (
            "the shape is right but this is a different part of the film."
            f" Hint: rows first, then columns: xray[{first_row}:{end_row},"
            f" {first_col}:{end_col}]."
        )
    return report(name, [problem])


def _fraction_problem(label, zone, other_zone, level, answer):
    """Describe what is wrong with one zone's dark fraction, or return None."""
    if is_placeholder(answer):
        return f"`{label}` is still `...`."
    dark = zone < level
    expected = float(dark.mean())
    if near(answer, expected):
        return None
    if isinstance(answer, np.ndarray):
        return (
            f"`{label}` is a whole array of {answer.shape}, but a single number is"
            " expected. Hint: count the True pixels with .sum(), then divide by"
            " the number of pixels, .size."
        )
    problem = f"`{label}` should be {expected:.4f}, got {answer!r}."
    if near(answer, dark.sum()):
        hint = (
            "that is the number of dark pixels, not the fraction. Divide it by"
            " the number of pixels in the zone, zone.size."
        )
    elif near(answer, expected * 100):
        hint = "that is a percentage. A fraction runs from 0 to 1, so do not multiply by 100."
    elif near(answer, (zone <= level).mean()):
        hint = "<= also counts pixels exactly equal to level. Darker than means <."
    elif near(answer, (zone > level).mean()) or near(answer, (zone >= level).mean()):
        hint = "you counted the bright pixels. Darker than level means zone < level."
    elif near(answer, (other_zone < level).mean()):
        hint = "that is the other zone's fraction. Are right and left swapped?"
    else:
        hint = (
            "make a mask with zone < level, then divide the number of True"
            " values (.sum()) by the number of pixels (.size)."
        )
    return f"{problem} Hint: {hint}"


def dark_fractions(right_lower, left_lower, level, right_fraction, left_fraction):
    name = "Dark fractions"
    if is_placeholder(right_fraction) and is_placeholder(left_fraction):
        return waiting(name)
    # Judge against the true zones, so an unfinished Problem 7.3 (left_lower
    # still holding the right zone) cannot make a wrong fraction look right.
    film = _lobar_film()
    for label, given, zone in (
        ("right_lower", right_lower, RIGHT_LOWER_ZONE),
        ("left_lower", left_lower, LEFT_LOWER_ZONE),
    ):
        if not (
            isinstance(given, np.ndarray) and np.array_equal(given, _crop(film, zone))
        ):
            return report(
                name,
                [
                    f"`{label}` is not the {label.replace('_', ' ')} zone of the lobar"
                    " pneumonia film. Finish Problem 7.3 first, then run this cell."
                ],
            )
    right_lower, left_lower = (
        _crop(film, RIGHT_LOWER_ZONE),
        _crop(film, LEFT_LOWER_ZONE),
    )
    problems = [
        problem
        for problem in (
            _fraction_problem(
                "right_fraction", right_lower, left_lower, level, right_fraction
            ),
            _fraction_problem(
                "left_fraction", left_lower, right_lower, level, left_fraction
            ),
        )
        if problem
    ]
    return report(name, problems)


def brightened(xray, amount, brighter):
    name = "Brightened film"
    if is_placeholder(brighter):
        return waiting(name)
    if not isinstance(brighter, np.ndarray):
        return report(name, [_not_an_array("brighter", brighter)])
    if brighter.shape != xray.shape:
        return report(
            name,
            [
                f"`brighter` should have the same shape as the film, {xray.shape},"
                f" got {brighter.shape}. Hint: brighten every pixel, not a slice."
            ],
        )
    expected = np.minimum(xray.astype(int) + amount, UINT8_MAX)
    if np.array_equal(brighter, expected):
        return report(name, [])
    wrapped = np.minimum((xray.astype(int) + amount) % (UINT8_MAX + 1), UINT8_MAX)
    if np.array_equal(brighter, wrapped):
        problem = (
            "pixels that were nearly white have turned dark. Hint: a uint8 array"
            " can only hold 0 to 255, so 250 + 60 wraps round to 54. Convert"
            " before you add: xray.astype(int) + amount."
        )
    elif brighter.max() > UINT8_MAX:
        problem = (
            "some pixels are above 255. Hint: keep the np.minimum line, which caps"
            " every pixel at 255 (pure white)."
        )
    elif np.array_equal(brighter, xray):
        problem = "the film is unchanged. Hint: add `amount` to every pixel."
    else:
        problem = (
            "each pixel should be its original value plus `amount`, capped at 255."
            " Hint: convert first with xray.astype(int), then add amount."
        )
    return report(name, [problem])


def _small_problem(film, step, small):
    expected = film[::step, ::step]
    if not isinstance(small, np.ndarray):
        return _not_an_array("small", small)
    if small.shape == expected.shape and np.array_equal(small, expected):
        return None
    problem = f"step 1: `small` should have shape {expected.shape}, got {small.shape}."
    if small.shape == film[:step, :step].shape:
        hint = (
            f":{step} takes only the first {step} rows. Two colons, ::{step},"
            f" take every {step}th row."
        )
    elif small.shape == film[::step].shape:
        hint = (
            "only the rows were downsampled. Do the columns too:"
            f" film[::{step}, ::{step}]."
        )
    elif small.shape == film.shape:
        hint = f"this is still full size. Keep every {step}th row and column."
    elif small.shape == expected.shape:
        problem = "step 1: `small` has the right shape but different pixels."
        hint = f"start from the first row and column: film[::{step}, ::{step}]."
    else:
        hint = f"keep every {step}th row and every {step}th column: film[::{step}, ::{step}]."
    return f"{problem} Hint: {hint}"


def _scaled_problem(small, scaled):
    expected = small / UINT8_MAX
    if not isinstance(scaled, np.ndarray):
        return _not_an_array("scaled", scaled)
    if scaled.shape != expected.shape:
        return (
            f"step 2: `scaled` should have the same shape as `small`,"
            f" {expected.shape}, got {scaled.shape}. Hint: scaling changes the"
            " values, not the shape."
        )
    if np.allclose(scaled, expected, rtol=0, atol=1e-6):
        return None
    if scaled.max() > 1:
        hint = "values go above 1. Divide by 255 so white becomes 1.0."
    elif not np.issubdtype(scaled.dtype, np.floating):
        hint = (
            "the values are whole numbers. // rounds down, so nearly every"
            " pixel becomes 0. Use / to keep the decimals."
        )
    elif np.allclose(scaled, small / small.max(), rtol=0, atol=1e-6):
        hint = (
            f"divide by 255, not by this film's own maximum ({small.max()})."
            " Every film should use the same scale, so a grey means the same"
            " number in every image."
        )
    else:
        hint = "divide `small` by 255, the largest value a uint8 can hold."
    return f"step 2: `scaled` has the wrong values. Hint: {hint}"


def _channels_problem(scaled, model_input):
    height, width = scaled.shape
    expected_shape = (height, width, 3)
    if not isinstance(model_input, np.ndarray):
        return _not_an_array("model_input", model_input)
    if model_input.shape != expected_shape:
        problem = (
            f"step 3: `model_input` should have shape {expected_shape},"
            f" got {model_input.shape}."
        )
        if model_input.shape == (3, height, width):
            hint = (
                "the channels are first. This model expects them last, so"
                " stack with axis=2."
            )
        elif model_input.shape == (height, width):
            hint = "there is still one channel. Stack three copies of `scaled`."
        else:
            hint = "use np.stack([scaled, scaled, scaled], axis=2)."
        return f"{problem} Hint: {hint}"
    expected = np.stack([scaled, scaled, scaled], axis=2)
    if np.allclose(model_input, expected, rtol=0, atol=1e-6):
        return None
    if model_input.max() > 1:
        hint = "stack `scaled`, not `small`, so the values stay between 0 and 1."
    else:
        hint = "each of the three channels should be an exact copy of `scaled`."
    return f"step 3: `model_input` has the wrong values. Hint: {hint}"


def prepared_input(film, step, small, scaled, model_input):
    name = "Model input"
    if is_placeholder(small):
        return waiting(name)
    expected_small = film[::step, ::step]
    steps = (
        ("small", small, lambda: _small_problem(film, step, small)),
        ("scaled", scaled, lambda: _scaled_problem(expected_small, scaled)),
        (
            "model_input",
            model_input,
            lambda: _channels_problem(expected_small / UINT8_MAX, model_input),
        ),
    )
    for number, (label, value, find_problem) in enumerate(steps, start=1):
        if is_placeholder(value):
            return report(
                name, [f"step {number}: `{label}` is still `...`. Replace it next."]
            )
        problem = find_problem()
        if problem:  # later steps build on this one, so report it alone
            return report(name, [problem])
    return report(name, [])


guard_checkers(globals())
