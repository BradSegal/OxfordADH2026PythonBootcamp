# MSc in Applied Digital Health: Python Bootcamp

**Python from scratch for digital health students.** University of Oxford, Applied Digital Health MSc, 2026 cohort.

---

Bradley Segal<br />
[bradley.segal@eng.ox.ac.uk](mailto:bradley.segal@eng.ox.ac.uk)<br />
Computational Health Informatics Lab<br />
Institute of Biomedical Engineering,<br />
Department of Engineering Science,<br />
University of Oxford

---

The text and exercises of the course are licensed under [CC BY 4.0](LICENSE-content.md) and the code under the [MIT licence](LICENSE). You are free to re-use and adapt both with appropriate attribution.

---

## Lab overview

This course is aimed at digital health students from clinical, technical, and other backgrounds who have never written a line of code. By the end of the course you will be able to read and write short programs in Python, work with patient-style data and images, and run a medical imaging AI model yourself. Just as importantly, you will be able to check code that someone else (or an AI assistant) has written for you.

All of this runs within [Google Colab](https://colab.research.google.com) which is a free service that lets you run Python within your web browser. No installation required.

## Instructions and lab sheet

Please follow the [lab sheet](ADH-Python_Bootcamp-Lab_sheet.pdf) for instructions on how to get started, the order of notebooks, and what each notebook requires from you. The below steps are the shortened version.

## How to start

1. Click the **Open in Colab** badge beside `00` in the table below.
2. Login with a Google account if asked by Colab. A personal account is fine.
3. Click **File > Save a copy in Drive**. This will open a copy of the notebook in a new tab; work in that one. If you don't do this your changes won't be saved.
4. Run the first code cell (the setup cell). You will get a warning that the notebook "was not authored by Google". Just click **Run anyway** as this is from the course. It takes ± 20 seconds to install the course helpers and will print out `Course helpers ready.`
5. Work down the notebook running each cell in turn with **Shift+Enter**.

Do the same for each notebook in the order below. You will get to Level 1 or 2 as part of the bootcamp practical and will need to work through the rest (Levels 2 to 8 and the MedVision lab) before the AI module starts on 16 November 2026.

## Learning path

| No. | Notebook | What you learn | Time | Open |
|-----|----------|----------------|------|------|
| 00 | Colab orientation | How notebooks, cells, and saving work | 10 min | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/BradSegal/OxfordADH2026PythonBootcamp/blob/main/notebooks/00_colab_orientation.ipynb) |
| 01 | Python basics | A guided tour through the core ideas prior to practising them | 45-60 min | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/BradSegal/OxfordADH2026PythonBootcamp/blob/main/notebooks/01_python_basics.ipynb) |
| 02 | Level 1: Values and variables | Arithmetic and named values: doses, BMI, fluid balance | 25 min | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/BradSegal/OxfordADH2026PythonBootcamp/blob/main/notebooks/02_L1_values_and_variables.ipynb) |
| 03 | Level 2: Strings | Working with text and building clear messages | 25 min | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/BradSegal/OxfordADH2026PythonBootcamp/blob/main/notebooks/03_L2_strings.ipynb) |
| 04 | Level 3: Decisions | Comparisons and `if` statements, such as BMI bands | 30 min | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/BradSegal/OxfordADH2026PythonBootcamp/blob/main/notebooks/04_L3_decisions.ipynb) |
| 05 | Level 4: Lists and loops | Handling a series of observations one at a time | 40 min | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/BradSegal/OxfordADH2026PythonBootcamp/blob/main/notebooks/05_L4_lists_and_loops.ipynb) |
| 06 | Level 5: Dictionaries | Records that pair names with values, like a patient record | 30 min | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/BradSegal/OxfordADH2026PythonBootcamp/blob/main/notebooks/06_L5_dictionaries.ipynb) |
| 07 | Level 6: Functions | Write a clinical rule once and use it everywhere | 40 min | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/BradSegal/OxfordADH2026PythonBootcamp/blob/main/notebooks/07_L6_functions.ipynb) |
| 08 | Level 7: Arrays and images | Grids of numbers and why an image is one | 45 min | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/BradSegal/OxfordADH2026PythonBootcamp/blob/main/notebooks/08_L7_arrays_and_images.ipynb) |
| 09 | Level 8: From a patient record to a model prompt | Summarising a patient safely, building a prompt, and reading library code | 45 min | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/BradSegal/OxfordADH2026PythonBootcamp/blob/main/notebooks/09_L8_bridge_to_medvision.ipynb) |
| 10 | MedVision lab | Asking a vision-language model about chest X-rays, and judging its answers | 75 min | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/BradSegal/OxfordADH2026PythonBootcamp/blob/main/notebooks/10_medvision_lab.ipynb) |
| Extension | Vibe-code a ward dashboard | Building a small tool with an AI assistant: specify, generate, test, debug | 75 min | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/BradSegal/OxfordADH2026PythonBootcamp/blob/main/extension/vibe_code_ward_dashboard.ipynb) |

These times are a guide for a first attempt; you can spend longer if you need to. Levels 1 through 8 build on top of each other and so should be attempted in sequence.

The MedVision lab works best with a free GPU (this is a graphics processor which makes the model fast). You can enable this within your copy by going to **Runtime > Change runtime type**, selecting **T4 GPU** and saving. Sometimes there isn't a free GPU that can be allocated to you by Colab. If this is the case, the lab will show pre-recorded responses from a compressed version of the same model (clearly labelled as saved), so you will still be able to work through all questions except for testing your own prompts.

## How the problems work

Each level has a handful of short problems where you **predict** what some code does before running it, **modify** working code, **make** something new, and **fix** code with a bug in it. Where you see `...` or `# Your code here` you need to replace that with your answer and then run the cell. The checker in that cell will tell you how you did:

- ✅ correct;
- ❌ not yet, with a hint that names the likely mistake; or
- ⏳ not attempted yet (where the starting code already runs, an unattempted problem shows ❌ with a hint instead).

You can run a cell as many times as you want. Nothing is marked or recorded; the checkers are there to help you learn. They will never block the notebook from running. If you get an error from your own code, read the last line, fix it, and rerun the cell.

## Solutions

Every notebook has a worked version with the answers filled in within the [`solutions/`](solutions/) folder (and [`extension/solutions/`](extension/solutions/) for the extension). Each has a Colab badge to open it directly.

Use them in a way that helps you learn. Make a real attempt and read the hint from the checker. If you're stuck after ± 10 minutes, look at the solution for that specific problem then close it and write the answer yourself. Once solved, compare your code to the solution, there's usually more than one good answer.

## Using the notebooks after the course

The notebooks are yours to keep. You'll find your saved copies within your Google Drive under the folder **Colab Notebooks**. If you want to start fresh, you can just open any notebook from the badge here again and save a new copy.

The setup cell installs the course helpers from this repository each time, so your copies will continue to function as long as this repository is online. If you want to re-use some of the ideas in your own work, copy the code you need into a new notebook rather than depending on the course helpers.

## Running on your own computer (optional)

Not required for the course. If you are already on Python 3.10 or above:

```bash
git clone https://github.com/BradSegal/OxfordADH2026PythonBootcamp.git
cd OxfordADH2026PythonBootcamp
python -m venv .venv
source .venv/bin/activate          # on Windows: .venv\Scripts\activate
pip install -e . jupyterlab        # use -e ".[vision]" for the MedVision lab
jupyter lab
```

With [uv](https://docs.astral.sh/uv/) the last four lines become `uv run --with jupyterlab jupyter lab`.

## A note on safety

The patient and ward records in this course are entirely fictional. The chest X-rays and associated short histories are published public domain teaching cases (see [their sources](src/adh_python/assets/SOURCES.md)). The code used in this course is teaching code intended to be read and learnt from and is not intended to be used to make decisions about actual patients. Clinical thresholds such as BMI bands or NEWS2 are included for teaching purposes only. The AI model used in the MedVision lab is a research model; never use its output for patient care.

## Licence

Copyright 2026 Bradley Segal. The course text and exercises (notebooks, lab sheet, and guides) are licensed under [CC BY 4.0](LICENSE-content.md); the code, including the `adh_python` package and the notebooks' code cells, under the [MIT licence](LICENSE). The bundled X-ray images are public domain (CC0); see [their sources](src/adh_python/assets/SOURCES.md).

Instructors: see [INSTRUCTORS.md](INSTRUCTORS.md).
