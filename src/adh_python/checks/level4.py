# SPDX-FileCopyrightText: 2026 Bradley Segal
# SPDX-License-Identifier: MIT

"""Checkers for Level 4: lists, indexing and loops.

Each checker takes the list the student worked on as well as their answer,
and recognises the classic loop mistakes: an accumulator reset inside the
loop, counting from 1, a stop position read as inclusive, and a "first match"
search that carries on to the last match.
"""

from __future__ import annotations

from adh_python import clinical
from adh_python.checks._core import check_value, guard_checkers, near


def _mean(values):
    return sum(values) / len(values)


def predict_slice(temperatures, prediction):
    expected = temperatures[1:3]
    if prediction == temperatures[0:2]:
        hint = "Positions start at 0, so position 1 is the second reading."
    elif prediction == temperatures[1:4]:
        hint = "The stop position is not included: [1:3] gives positions 1 and 2."
    elif prediction == temperatures[0:3]:
        hint = "Positions start at 0, and the stop position is not included."
    elif not isinstance(prediction, list):
        hint = "A slice of a list is a list. Write it in square brackets."
    else:
        hint = "[1:3] starts at position 1 and stops just before position 3."
    return check_value("Prediction", prediction, expected, hint=hint)


def mean_recent(respiration_rates, mean_rr):
    expected = _mean(respiration_rates[-3:])
    if near(mean_rr, _mean(respiration_rates)):
        hint = "That is the mean of every reading. Slice the list to keep only the last three."
    elif near(mean_rr, _mean(respiration_rates[:3])):
        hint = "[:3] gives the first three readings, the oldest. The most recent are at the end: [-3:]."
    elif near(mean_rr, sum(respiration_rates[-3:]) / len(respiration_rates)):
        hint = "Divide by the number of readings you added up (the length of the slice), not of the whole list."
    else:
        hint = "respiration_rates[-3:] gives the last three readings."
    return check_value("Mean of the last three", mean_rr, expected, hint=hint)


def count_scoring_spo2(spo2_readings, count):
    scores = [clinical.score_spo2_scale1(reading) for reading in spo2_readings]
    expected = sum(1 for score in scores if score > 0)
    if count == len(spo2_readings):
        hint = "You counted every reading. Put count += 1 inside the if, so it only runs when the reading scores."
    elif count == len(spo2_readings) - expected:
        hint = "You counted the readings that do not score. Check the comparison in your if."
    elif count in (0, 1):
        hint = "Is count = 0 inside the loop? Set it once, before the loop, or it starts again every round."
    else:
        hint = "Add 1 for each reading where clinical.score_spo2_scale1(reading) is above 0."
    return check_value("Readings that score", count, expected, hint=hint)


def first_apyrexial(temperatures, times, first_time):
    scores = [clinical.score_temperature(temperature) for temperature in temperatures]
    matches = [index for index, score in enumerate(scores) if score == 0]
    scoring = [index for index, score in enumerate(scores) if score != 0]
    expected = times[matches[0]] if matches else None
    last_match = matches and first_time == times[matches[-1]]
    # A reversed condition (!= 0 or > 0) stores the time of a round that
    # still scores: the first one with break, the last one without.
    reversed_condition = scoring and first_time in (
        times[scoring[0]],
        times[scoring[-1]],
    )
    if first_time is None:
        hint = "Nothing was stored. Check the condition: you want a temperature score of 0."
    elif reversed_condition and last_match:
        # Jordan's first and last rounds are both at 06:00, so either mistake
        # gives this time.
        hint = (
            f"Two rounds were at {first_time}: one whose temperature still scores"
            " on NEWS2, and the last round. Either mistake gives this time, so"
            " check two things: the condition should be"
            " clinical.score_temperature(temperatures[i]) == 0, and break after"
            " storing the time, so the loop stops at the first match."
        )
    elif reversed_condition:
        hint = (
            f"At {first_time} the temperature still scored on NEWS2. The condition"
            " is the wrong way round: you want"
            " clinical.score_temperature(temperatures[i]) == 0."
        )
    elif last_match:
        hint = "That is the last matching round, not the first. Add break after storing the time, so the loop stops at the first match."
    elif first_time in matches:
        hint = "That is the position in the list. Use it to look up the time: times[i]."
    elif first_time in temperatures:
        hint = (
            "That is the temperature. Store the time of that round instead: times[i]."
        )
    else:
        hint = "Loop over the positions, and store times[i] for the first temperature that scores 0."
    return check_value("First apyrexial round", first_time, expected, hint=hint)


def convert_temperatures(readings_f, readings_c):
    exact = [clinical.fahrenheit_to_celsius(reading) for reading in readings_f]
    expected = [round(celsius, 1) for celsius in exact]
    if readings_c == []:
        hint = "The list is still empty. Call readings_c.append(...) inside the loop."
    elif isinstance(readings_c, list) and len(readings_c) == 1:
        hint = (
            "Only one value was kept. Is readings_c = [] inside the loop, starting"
            " the list again each round, or is append outside the loop?"
        )
    elif isinstance(readings_c, list) and len(readings_c) == len(exact):
        same = all(map(near, readings_c, exact))
        hint = (
            "Round each value to one decimal place with round(celsius, 1)."
            if same
            else "Subtract 32 first, then multiply by 5 / 9. Brackets control the order."
        )
    else:
        hint = "Start with an empty list before the loop, then append one converted value per reading."
    return check_value("Temperatures in °C", readings_c, expected, hint=hint)


def mean_pulse(pulses, mean):
    expected = _mean(pulses)
    if near(mean, pulses[-1] / len(pulses)):
        hint = (
            "Only the last reading was added up. Is total = 0 inside the loop?"
            " Set it once, before the loop starts."
        )
    elif near(mean, sum(pulses[1:]) / len(pulses)):
        hint = "The first reading was skipped. Positions start at 0, so range(len(pulses)) starts there too."
    else:
        hint = "Add every reading to total, then divide by how many readings there are."
    return check_value("Mean pulse", mean, expected, hint=hint)


guard_checkers(globals())
