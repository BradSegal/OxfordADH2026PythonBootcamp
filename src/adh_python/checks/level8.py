# SPDX-FileCopyrightText: 2026 Bradley Segal
# SPDX-License-Identifier: MIT

"""Checkers for Level 8: the bridge to MedVision.

Students turn a patient record into a short, de-identified summary, build an
imaging prompt from it, and read the package's own model wrapper. Each checker
calls the student's function on more than one patient, so a hard-coded answer
or a leaked identifier is caught.
"""

from __future__ import annotations

import re

from adh_python.checks._core import (
    article,
    check_value,
    guard_checkers,
    is_placeholder,
    report,
    waiting,
)
from adh_python.data import sample_patient
from adh_python.imaging import vlm

IDENTIFIERS = ("name", "hospital_number")
NOT_NEEDED = {
    "ward": "the ward says where the patient is, not what the X-ray shows.",
    "bed": "the bed number locates the patient; the model does not need it.",
    "consultant": "the consultant's name identifies a person and does not help "
    "read the film.",
    "pronouns": "pronouns are not needed to read a chest X-ray.",
    "height_m": "height is not needed to read a chest X-ray.",
    "weight_kg": "weight is not needed to read a chest X-ray.",
    "medications": "the medication list is not needed to read a chest X-ray.",
    "allergies": "allergies matter for prescribing, not for reading the film.",
    "consults": "the list of consults is not needed to read a chest X-ray.",
    "outstanding_tasks": "the task list is not needed to read a chest X-ray.",
}


def _second_patient() -> dict:
    """A different patient, so hard-coded values and first readings show up."""
    patient = sample_patient()
    patient.update(
        name="Ada Okafor",
        hospital_number="RTH-551177",
        age=71,
        diagnosis="Exacerbation of COPD",
    )
    patient["observations"].update(
        respiration_rate=[18, 21, 23],
        spo2=[94, 92, 89],
        temperature=[37.1, 37.9, 38.4],
    )
    return patient


def _latest(patient: dict, key: str):
    return patient["observations"][key][-1]


def _first(patient: dict, key: str):
    return patient["observations"][key][0]


def predict_summary(prediction):
    patient = sample_patient()
    expected = (
        f"{patient['name']} ({patient['hospital_number']}), "
        f"{patient['age']}, {patient['diagnosis']}"
    )
    return check_value(
        "Prediction",
        prediction,
        expected,
        hint="Each {...} is replaced by the value stored under that key; the "
        "brackets, commas and spaces outside the braces are printed as typed.",
    )


def minimal_fields(fields_to_send):
    name = "Minimal fields"
    if is_placeholder(fields_to_send):
        return waiting(name)
    if not isinstance(fields_to_send, list):
        return report(
            name,
            [f"expected a list of keys, got {article(type(fields_to_send).__name__)}."],
        )
    problems = []
    for key in fields_to_send:
        if key in IDENTIFIERS:
            problems.append(
                f"{key!r} identifies the patient. Never send a name or hospital "
                "number to a model; it does not need them to read the film."
            )
        elif key in NOT_NEEDED:
            problems.append(f"remove {key!r}: {NOT_NEEDED[key]}")
        elif key not in ("age", "diagnosis", "observations"):
            problems.append(f"{key!r} is not a key in the patient record.")
    for key in ("age", "diagnosis"):
        if key not in fields_to_send:
            problems.append(
                f"keep {key!r}: the model needs it to put the image in context."
            )
    return report(name, problems)


def summarise_patient(function):
    name = "summarise_patient"
    if is_placeholder(function):
        return waiting(name)
    if not callable(function):
        return report(
            name, [f"expected a function, got {article(type(function).__name__)}."]
        )
    problems = []
    for patient in (sample_patient(), _second_patient()):
        try:
            summary = function(patient)
        except Exception as error:  # report any student error in plain English
            problems.append(f"summarise_patient raised {type(error).__name__}: {error}")
            continue
        if is_placeholder(summary):  # the scaffold still returns ...
            return waiting(name)
        if summary is None:
            problems.append(
                "summarise_patient returned None. Did you forget to `return` "
                "the summary?"
            )
            break
        if not isinstance(summary, str):
            problems.append(
                f"the summary should be text (a str), got {article(type(summary).__name__)}."
            )
            break
        problems += _summary_problems(patient, summary)
    return report(name, list(dict.fromkeys(problems)))


# The labels a student might write before each number, so a number is judged
# by the label in front of it rather than found anywhere in the text. Labels
# of other observations only mark where one number's text ends.
_LABELS = {
    "respiration_rate": (
        "respiratory rate",
        "respiration rate",
        "breathing rate",
        "resp rate",
        "resp",
        "rr",
    ),
    "spo2": (
        "oxygen saturations",
        "oxygen saturation",
        "o2 saturations",
        "o2 saturation",
        "saturations",
        "saturation",
        "o2 sats",
        "sats",
        "spo2",
        "o2",
    ),
    "temperature": ("temperature", "temp", "t"),
    None: (
        "pulse",
        "heart rate",
        "hr",
        "blood pressure",
        "systolic bp",
        "systolic",
        "bp",
        "pain score",
        "pain",
        "consciousness",
        "avpu",
    ),
}
_LABEL_KEY = {label: key for key, labels in _LABELS.items() for label in labels}
_LABEL_PATTERN = re.compile(
    r"\b("
    + "|".join(re.escape(label) for label in sorted(_LABEL_KEY, key=len, reverse=True))
    + r")\b"
)
# A whole number such as 17 or 36.8, not part of a longer one or of "SpO2".
_NUMBER = re.compile(r"(?<![\w.\-])\d+(?:\.\d+)?")
_DESCRIPTIONS = {
    "respiration_rate": ("respiratory rate", "respiratory rate {}/min"),
    "spo2": ("oxygen saturation", "SpO2 {}%"),
    "temperature": ("temperature", "temperature {} °C"),
}


def _plain(text: str) -> str:
    """Lower case, with hyphens and underscores as spaces, keeping positions.

    A minus sign attached to a digit (ASCII, Unicode minus or en dash) is kept
    as "-", so "-17" or "−17" is not read as 17; a spaced dash, as in
    "RR - 17", is punctuation. A subscript two (as in SpO₂) becomes 2.
    """
    text = re.sub(r"[\u2212\u2013](?=\d)", "-", text.lower())
    text = re.sub(r"[-\u2212\u2013](?!\d)", " ", text)
    return text.replace("_", " ").replace("₂", "2")


def _numbers_after_labels(summary: str) -> dict:
    """For each observation, the numbers written after the first label for it.

    The numbers run up to the next label of a different observation, so
    "SpO2 96%, temperature 36.8" gives [96] for spo2 and [36.8] for temperature.
    """
    text = _plain(summary)
    labels = [(m, _LABEL_KEY[m.group(1)]) for m in _LABEL_PATTERN.finditer(text)]
    numbers = [(m.start(), m.group()) for m in _NUMBER.finditer(text)]
    found = {}
    for index, (match, key) in enumerate(labels):
        if key is None or key in found:
            continue
        end = next(
            (m.start() for m, other in labels[index + 1 :] if other != key),
            len(text),
        )
        found[key] = [n for position, n in numbers if match.end() <= position < end]
    return found


def _same_number(text: str, value) -> bool:
    return abs(float(text) - float(value)) < 1e-9


def _summary_problems(patient: dict, summary: str) -> list[str]:
    problems = []
    first_name, *_, surname = patient["name"].split()
    for leaked in (patient["hospital_number"], first_name, surname):
        if leaked.casefold() in summary.casefold():
            problems.append(
                f"the summary contains {leaked!r}. Leave out the name and "
                "hospital number: the model does not need them, and they would "
                "leave the hospital with the prompt."
            )
    all_numbers = _NUMBER.findall(_plain(summary))
    if not any(_same_number(n, patient["age"]) for n in all_numbers):
        problems.append(
            f"the summary should include the age ({patient['age']}) as a number "
            "of its own. Did you type a number instead of using patient['age']?"
        )
    if _plain(" ".join(patient["diagnosis"].split())) not in " ".join(
        _plain(summary).split()
    ):
        problems.append(
            f"the summary should include the diagnosis ({patient['diagnosis']!r})."
        )
    after_labels = _numbers_after_labels(summary)
    for key, (label, example) in _DESCRIPTIONS.items():
        readings = patient["observations"][key]
        latest = readings[-1]
        earlier = [r for r in readings[:-1] if not _same_number(str(r), latest)]
        numbers = after_labels.get(key, [])
        if not numbers:
            problems.append(
                f"the summary should include the latest {label} ({latest}), "
                f"straight after its label, for example {example.format(latest)!r}."
            )
        elif not _same_number(numbers[0], latest):
            if any(_same_number(numbers[0], r) for r in earlier):
                problems.append(
                    f"the {label} is an earlier reading ({numbers[0]}), not the "
                    f"latest ({latest}). Use [-1] for the last item in a list."
                )
            else:
                problems.append(
                    f"the {label} should be {latest}, the latest reading, but the "
                    f"number after its label is {numbers[0]}. Check that you used "
                    "the right key and that nothing is added to the number."
                )
        elif any(_same_number(n, r) for n in numbers[1:] for r in earlier):
            problems.append(
                f"the {label} is followed by earlier readings as well. Send only "
                "the latest: [-1] gives the last item, not the whole list."
            )
    if len(summary) >= 300:
        problems.append(
            f"the summary is {len(summary)} characters long. Keep it under 300: "
            "send what the model needs, nothing more."
        )
    return problems


_PROMPT_CASES = [
    (
        "54-year-old, community-acquired pneumonia",
        "the lungs",
        "Is there consolidation?",
    ),
    ("71-year-old, exacerbation of COPD", "the heart", "Is the heart enlarged?"),
]


def build_imaging_prompt(function):
    name = "build_imaging_prompt"
    if is_placeholder(function):
        return waiting(name)
    if not callable(function):
        return report(
            name, [f"expected a function, got {article(type(function).__name__)}."]
        )
    problems = []
    for summary, focus, question in _PROMPT_CASES:
        expected = vlm.build_prompt(summary, focus, question)
        try:
            prompt = function(summary, focus, question)
        except Exception as error:  # report any student error in plain English
            problems.append(
                f"build_imaging_prompt raised {type(error).__name__}: {error}"
            )
            continue
        if is_placeholder(prompt):  # the scaffold still returns ...
            return waiting(name)
        if prompt is None:
            problems.append(
                "build_imaging_prompt returned None. Did you forget to `return` "
                "the prompt?"
            )
            break
        if prompt != expected:
            problems.append(_prompt_problem(prompt, expected, summary, focus, question))
    if not problems:
        problems = _empty_question_problem(function)
    return report(name, list(dict.fromkeys(problems)))


def _prompt_problem(prompt, expected, summary, focus, question) -> str:
    if not isinstance(prompt, str):
        return (
            f"the prompt should be text (a str), got {article(type(prompt).__name__)}."
        )
    for label, value in (
        ("summary", summary),
        ("focus", focus),
        ("question", question),
    ):
        if value not in prompt:
            return (
                f"the prompt does not contain the {label} it was given ({value!r}). "
                f"Use the parameter `{label}` rather than typing fixed text."
            )
    if prompt.count("\n") != 3:
        return (
            "the prompt should have four lines. Put \\n between the parts, "
            "and none after the last line."
        )
    if not prompt.endswith(expected.splitlines()[-1]):
        return "the last line should be the instruction exactly as given."
    return (
        f"the prompt should be exactly:\n{expected}\n     but yours is:\n{prompt}\n"
        "     Check the labels, spaces and punctuation."
    )


def _empty_question_problem(function) -> list[str]:
    try:
        function("54-year-old, community-acquired pneumonia", "the lungs", "")
    except ValueError:
        return []
    except Exception as error:  # report any student error in plain English
        return [
            f"with an empty question it raised {type(error).__name__}; "
            "raise ValueError instead."
        ]
    return [
        'with an empty question ("") it should raise ValueError: a prompt '
        "with no question wastes a model run."
    ]


def reading_vlm(env_variable, no_gpu_result, prompt_function, max_tokens):
    name = "Reading vlm.py"
    answers = (env_variable, no_gpu_result, prompt_function, max_tokens)
    if any(is_placeholder(answer) for answer in answers):
        return waiting(name)
    problems = []
    if env_variable != "ADH_VLM_MODEL":
        problems.append(
            "the environment variable is the name inside os.environ.get(...) in "
            "model_name(). Copy it exactly, in quotes."
        )
    if no_gpu_result is not None:
        if no_gpu_result == "None":
            hint = "write None without quotes: it is a value, not text."
        elif no_gpu_result is False:
            hint = "look again: load_model returns None, not False."
        else:
            hint = "find `if name == DEFAULT_MODEL and not gpu:` in load_model."
        problems.append(f"without a GPU, load_model returns None; {hint}")
    function_name = str(prompt_function).removeprefix("vlm.").removesuffix("()")
    if function_name != "build_prompt":
        problems.append(
            "the function that builds the prompt from a summary, focus and "
            "question is the one whose name starts with `build_`."
        )
    if max_tokens != vlm.MAX_NEW_TOKENS:
        problems.append(
            "the longest reply is set by MAX_NEW_TOKENS near the top of the file. "
            "Give the number, without quotes."
        )
    return report(name, problems)


def _third_patient() -> dict:
    """A third patient for imaging_request, with a different age and diagnosis."""
    patient = sample_patient()
    patient.update(
        name="Leah Khan",
        hospital_number="RTH-330412",
        age=38,
        diagnosis="Suspected spontaneous pneumothorax",
    )
    return patient


_REQUEST_CASES = [
    (sample_patient, "the lungs", "Is there consolidation?"),
    (_second_patient, "the heart", "Is the heart enlarged?"),
    (_third_patient, "the pleura and the lung edges", "Is there a pneumothorax?"),
]


def imaging_request(function):
    name = "imaging_request"
    if is_placeholder(function):
        return waiting(name)
    if not callable(function):
        return report(
            name, [f"expected a function, got {article(type(function).__name__)}."]
        )
    problems = []
    for make_patient, focus, question in _REQUEST_CASES:
        patient = make_patient()
        summary = f"{patient['age']}-year-old, {patient['diagnosis']}"
        expected = vlm.build_prompt(summary, focus, question)
        try:
            prompt = function(patient, focus, question)
        except Exception as error:  # report any student error in plain English
            problems.append(f"imaging_request raised {type(error).__name__}: {error}")
            continue
        if is_placeholder(prompt):
            return waiting(name)
        if not isinstance(prompt, str):
            return report(
                name,
                ["imaging_request should return the prompt text from build_prompt."],
            )
        if prompt != expected:
            problems.append(_request_problem(patient, prompt, expected))
            break  # one patient is enough to show the mistake
    return report(name, problems)


def _request_problem(patient, prompt, expected) -> str:
    lines, wanted = prompt.splitlines(), expected.splitlines()
    focus_line, question_line = wanted[1], wanted[2]
    if f"Focus: {question_line.removeprefix('Question: ')}" in prompt:
        return (
            "the focus line holds the question. Arguments are matched by "
            "position, so they must be in the order build_prompt expects "
            "(patient_summary, focus, question), or named: focus=..., question=...."
        )
    first_name, *_, surname = patient["name"].split()
    if any(
        part in prompt for part in (first_name, surname, patient["hospital_number"])
    ):
        return "the prompt contains an identifier; leave it out."
    if not lines or lines[0] != wanted[0]:
        return (
            f"the first line should be {wanted[0]!r}. Keep the `summary = ...` "
            "line as given and pass `summary` to build_prompt: the bug is "
            "elsewhere."
        )
    if focus_line not in lines or question_line not in lines:
        return "the prompt should have the focus and question on their own lines."
    return f"the prompt should be exactly:\n{expected}\n     but yours is:\n{prompt}"


guard_checkers(globals())
