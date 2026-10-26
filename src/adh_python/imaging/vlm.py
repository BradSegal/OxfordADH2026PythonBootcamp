# SPDX-FileCopyrightText: 2026 Bradley Segal
# SPDX-License-Identifier: MIT

"""MedVision: ask a vision-language model about a chest X-ray.

A vision-language model reads an image and a written prompt and replies in
text. This module wraps one such model, MedGemma 1.5 4B, in a few functions:

    gpu_available()   is there a GPU to run the model on?
    load_model()      download and load the model (it needs a GPU)
    build_prompt()    turn patient details, a focus and a question into a prompt
    describe()        show the model an X-ray and print its reply as it arrives
    saved_report()    a reply recorded earlier, for when there is no GPU

Torch and transformers are imported inside the functions that need them, so
`import adh_python` stays quick.
"""

from __future__ import annotations

import json
import os
from importlib.resources import files
from pathlib import Path

from adh_python.imaging.images import IMAGES, image_path

DEFAULT_MODEL = "unsloth/medgemma-1.5-4b-it"
MAX_NEW_TOKENS = 400  # the longest reply, in tokens (a token is about 3/4 of a word)

# The focus and question used for a first read with build_prompt().
FOCUS = "the lungs, heart and pleura"
QUESTION = "What is the main abnormality, if there is one?"

# The standard prompts used in the lab. Each of the first four makes a single
# change to the one before it, so you can see what each change does.
_PERSONA = "You are a consultant radiologist reporting for a ward team."
_LOOK = f"Look at {FOCUS} on this chest X-ray. {QUESTION}"
_STRUCTURE = (
    "Reply in three short sections: Findings, Impression, "
    "and Confidence (low, medium or high)."
)
PROMPTS = {
    "describe": "Describe this chest X-ray.",
    "focused": _LOOK,
    "persona": f"{_PERSONA} {_LOOK}",
    "structured": f"{_PERSONA} {_LOOK} {_STRUCTURE}",
    "pneumothorax": "Is there a pneumothorax on this chest X-ray?",
    "leading_mass": (
        "Describe the size and position of the mass in the left upper zone "
        "on this chest X-ray."
    ),
}

NO_GPU_MESSAGE = """\
No GPU found, so the model has not been loaded.

That is fine: every cell in this notebook still runs. Where the model would
reply, you will see a reply saved earlier instead. To run the model yourself,
choose Runtime > Change runtime type > T4 GPU, then run the notebook again."""

LOAD_FAILED_MESSAGE = """\
The model could not be loaded ({error}).

This is usually a download that was interrupted or blocked, or a GPU that ran
out of memory. You can carry on: every cell in this notebook still runs, and
where the model would reply you will see a reply saved earlier instead. To try
again, choose Runtime > Restart session, then run the notebook from the top."""


def model_name() -> str:
    """The model to load: ADH_VLM_MODEL if that is set, otherwise MedGemma."""
    return os.environ.get("ADH_VLM_MODEL", DEFAULT_MODEL)


def gpu_available() -> bool:
    """True if PyTorch is installed and can see a GPU."""
    try:
        import torch
    except ImportError:
        return False
    return torch.cuda.is_available()


def load_model(name: str | None = None) -> dict | None:
    """Load the model and its processor, or return None if that is not possible.

    The result is a plain dict: {"name": ..., "model": ..., "processor": ...}.
    The full model needs a GPU. A tiny test model, chosen with the ADH_VLM_MODEL
    environment variable, also runs on an ordinary CPU. Without a GPU, or if
    the download or loading fails, it explains why and returns None, so the
    notebook can carry on with the saved replies.
    """
    name = name or model_name()
    gpu = gpu_available()
    if name == DEFAULT_MODEL and not gpu:
        print(NO_GPU_MESSAGE)
        return None

    print(f"Loading {name}. The first time, the download takes a few minutes.")
    try:
        import torch
        from transformers import AutoModelForImageTextToText, AutoProcessor

        model = AutoModelForImageTextToText.from_pretrained(
            name,
            dtype=torch.bfloat16 if gpu else torch.float32,
            device_map="auto" if gpu else None,
        )
        processor = AutoProcessor.from_pretrained(name)
    except Exception as error:  # a failed download must not stop the lab
        detail = (str(error).splitlines() or [""])[0][:200]
        print(LOAD_FAILED_MESSAGE.format(error=f"{type(error).__name__}: {detail}"))
        return None
    print("Model ready.")
    return {"name": name, "model": model, "processor": processor}


def build_prompt(patient_summary: str, focus: str, question: str) -> str:
    """Combine minimal patient details, a focus and a question into one prompt.

    The patient summary should hold only what the model needs (age, presenting
    problem, key observations), never a name or hospital number.
    """
    if not question.strip():
        raise ValueError("the prompt needs a question")
    return (
        f"Clinical details: {patient_summary}\n"
        f"Focus: {focus}\n"
        f"Question: {question}\n"
        "Describe only what you can see on the image, and say if you are unsure."
    )


def describe(
    model: dict | None,
    image: str | Path,
    prompt: str,
    max_new_tokens: int = MAX_NEW_TOKENS,
) -> str:
    """Show the model one X-ray and a prompt; print its reply and return it.

    `image` is a name from IMAGES (such as "normal") or the path to an image
    file. If `model` is None (no GPU), the saved reply for this image and
    prompt is shown instead, when there is one.
    """
    if model is None:
        return _show_saved_reply(image, prompt)

    import torch
    from PIL import Image
    from transformers import TextStreamer

    path = image_path(image) if image in IMAGES else Path(image)
    picture = Image.open(path).convert("RGB")
    messages = [
        {
            "role": "user",
            "content": [
                {"type": "image", "image": picture},
                {"type": "text", "text": prompt},
            ],
        }
    ]
    processor, network = model["processor"], model["model"]
    inputs = processor.apply_chat_template(
        messages,
        add_generation_prompt=True,
        tokenize=True,
        return_dict=True,
        return_tensors="pt",
    ).to(network.device, dtype=network.dtype)
    # The streamer prints each word as it is generated, so you are not left
    # waiting in silence. do_sample=False always picks the most likely next
    # token, so the same prompt gives the same reply each time.
    streamer = TextStreamer(
        processor.tokenizer, skip_prompt=True, skip_special_tokens=True
    )
    with torch.inference_mode():
        output = network.generate(
            **inputs,
            max_new_tokens=max_new_tokens,
            do_sample=False,
            streamer=streamer,
        )
    new_tokens = output[0][inputs["input_ids"].shape[-1] :]
    return processor.decode(new_tokens, skip_special_tokens=True).strip()


def saved_reports() -> dict:
    """Every saved reply, with a record of how and when it was made."""
    path = files("adh_python") / "assets" / "reference_outputs.json"
    return json.loads(path.read_text(encoding="utf-8"))


def saved_report(image_name: str, prompt_id: str) -> str:
    """The saved reply for a bundled image and a prompt from PROMPTS."""
    outputs = saved_reports()["outputs"]
    if image_name not in outputs:
        raise KeyError(f"no saved replies for {image_name!r}; try {sorted(outputs)}")
    if prompt_id not in outputs[image_name]:
        raise KeyError(
            f"no saved reply for prompt {prompt_id!r}; "
            f"try {sorted(outputs[image_name])}"
        )
    return outputs[image_name][prompt_id]["text"]


def _show_saved_reply(image: str | Path, prompt: str) -> str:
    for saved in saved_reports()["outputs"].get(str(image), {}).values():
        if saved["prompt"] == prompt:
            print(f"[{saved_reports()['provenance']['label']}]\n")
            print(saved["text"])
            return saved["text"]
    print(
        "No model is loaded, and there is no saved reply for this exact image "
        "and prompt. Saved replies exist only for the standard prompts and the "
        "bundled images. To try your own prompt, run this notebook on a GPU."
    )
    return ""
