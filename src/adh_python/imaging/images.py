# SPDX-FileCopyrightText: 2026 Bradley Segal
# SPDX-License-Identifier: MIT

"""The bundled teaching X-rays and what each one shows.

Every image is a CC0 file from Wikimedia Commons, converted to 8-bit
greyscale PNG and resized to at most 1024 pixels on its longest side.
`findings` follows the uploader's own description closely (normal_2 is
captioned only "Chest X-ray PA", so its reading is the course's), and is the
reference answer students compare the model's report against. Full
provenance is in adh_python/assets/SOURCES.md.
"""

from __future__ import annotations

from importlib.resources import files
from pathlib import Path

IMAGES = {
    "normal": {
        "file": "chest_normal_pa.png",
        "view": "PA",
        "patient": "21-year-old woman, left chest pain after a collision playing football",
        "findings": "Normal chest radiograph, no sign of injury.",
        "abnormal": False,
    },
    "normal_2": {
        "file": "chest_normal_pa_2.png",
        "view": "PA",
        "patient": "Adult, no clinical details recorded",
        "findings": "No abnormality described (the uploader's caption is only "
        "'Chest X-ray PA'); read as a normal chest radiograph for this course.",
        "abnormal": False,
    },
    "lobar_pneumonia": {
        "file": "chest_lobar_pneumonia.png",
        "view": "PA",
        "patient": "67-year-old man",
        "findings": "Lobar pneumonia affecting the right middle lobe.",
        "abnormal": True,
    },
    "multifocal_consolidation": {
        "file": "chest_multifocal_consolidation.png",
        "view": "PA",
        "patient": "88-year-old man, a week of fever, fatigue and mild cough; "
        "influenza A and Haemophilus influenzae detected",
        "findings": "Multifocal, patchy consolidation, mainly in the right upper lobe.",
        "abnormal": True,
    },
    "heart_failure": {
        "file": "chest_heart_failure.png",
        "view": "PA",
        "patient": "83-year-old man with previous coronary artery bypass grafting, "
        "presenting with laboured breathing",
        "findings": "Distinct Kerley B lines, an enlarged heart, somewhat "
        "dilated pulmonary vessels and a minor pleural effusion (seen, for "
        "example, in the right horizontal fissure); no obvious lung oedema. "
        "Read as intermediate (stage II) heart failure. Sternotomy wires from "
        "the previous cardiac surgery are also visible.",
        "abnormal": True,
    },
}


def image_path(name: str) -> Path:
    """Path to a bundled X-ray, for example image_path("lobar_pneumonia")."""
    if name not in IMAGES:
        raise KeyError(f"unknown image {name!r}; choose from {sorted(IMAGES)}")
    return Path(str(files("adh_python") / "assets" / "images" / IMAGES[name]["file"]))
