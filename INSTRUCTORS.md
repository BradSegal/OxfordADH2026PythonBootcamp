# Notes for instructors and facilitators

This guide is intended for anyone running or supporting the bootcamp. Students should start from [README.md](README.md) which links out to everything they need.

The [lab sheet](ADH-Python_Bootcamp-Lab_sheet.pdf) is intended as a student guide for the course as a whole. This page is intended for whoever is running the session.

## The bootcamp day

The day consists of two 75-minute sessions, the first being a lecture followed by a supervised practical session. Students then complete the residual notebooks in their own time prior to the AI module running from 16 November 2026.

### Session 1: lecture (75 minutes)

| Time | Topic | Aim |
|------|-------|-----|
| 0-15 | Why learn Python if AI can write code? | AI assistants write plausible code quickly. Some of it is wrong. Someone has to say precisely what they want, read what comes back, test it, and decide if it's safe to use. That is the skill this course builds. It is similar to checking a confident junior's drug chart. |
| 15-50 | Fundamentals, live in Colab | Teach three ideas properly: variables, lists with a `for` loop, and `if`/`elif`/`else`. Preview the rest (text, dictionaries, functions) in a minute each; the notebooks teach them. Keep one clinical example running through, such as a set of observations, and ask the room to predict each output before you run it. |
| 50-70 | Problem decomposition | Take one clinical question (e.g., "Which patients have had their temperature rise over one degree from admission?") and break it up into inputs, outputs, steps, edge cases, and test cases prior to writing any code. Demonstrate that the same plan is what you would give to an AI assistant and how the test cases can be used to verify the response. |
| 70-75 | Getting ready | Everyone has `00` opened from the badge in the README and has signed in and made a copy so that we can start the practical on time. |

Live code rather than showing slides of code and let mistakes happen, it's part of the lesson to read an error message aloud and fix it.

### Session 2: practical (75 minutes)

| Time | Notebook | Notes |
|------|----------|-------|
| 0-10 | `00_colab_orientation` | Walk the room. Check every student is working in their own copy (the tab title starts "Copy of"). |
| 10-45 | `01_python_basics` | Guided walkthrough, students run and modify the examples. Full walkthrough is 45-60 mins so stop after loops and defer functions to home. |
| 45-75 | `02_L1_values_and_variables`, then `03_L2_strings` | Most students complete Level 1 and start Level 2, however, everything after this point is homework and clarifying this at the beginning prevents anyone from feeling as if they're behind. |

### Before 16 November 2026 (self-paced)

Students will complete Level 2 and then progress through Levels 3 to 8 (`04` to `09`) and then the MedVision lab (`10`). Encourage them to do a little bit often: one level per sitting works well.

## Timings for each notebook

These are first attempt estimates for a student with no programming experience. Faster students take about half as long.

| Notebook | Time | Where |
|----------|------|-------|
| `00_colab_orientation` | 10 min | Practical |
| `01_python_basics` | 45-60 min | Practical (finish at home) |
| `02_L1_values_and_variables` | 25 min | Practical |
| `03_L2_strings` | 25 min | Practical or self-paced |
| `04_L3_decisions` | 30 min | Self-paced |
| `05_L4_lists_and_loops` | 40 min | Self-paced |
| `06_L5_dictionaries` | 30 min | Self-paced |
| `07_L6_functions` | 40 min | Self-paced |
| `08_L7_arrays_and_images` | 45 min | Self-paced |
| `09_L8_bridge_to_medvision` | 45 min | Self-paced |
| `10_medvision_lab` | 75 min | Self-paced, GPU recommended |
| `extension/vibe_code_ward_dashboard` | 75 min | Separate guided session (see `extension/FACILITATOR.md`) |

## Facilitator tips

- **Save a copy first.** In the first ten minutes, ensure all screens have a tab starting with "Copy of". Not saving a copy is the one mistake that loses work.
- **Ask for a prediction before a run.** "What do you think this prints?" forces a student to read the code, and a wrong prediction is the moment they learn.
- **Read the checker together.** Each ❌ comes with a hint indicating what is likely the mistake. Point students to this before explaining it yourself.
- **Do not take the keyboard.** Ask them a question that leads to the fix and let them type it.
- **Frame errors as information.** Typically the last line of a red error message is the reason something failed. Role model reading it calmly.
- **Pair students up** where one is stuck and a neighbour has just solved the same problem; explaining it helps both.
- **For students that finish early,** suggest they attempt the next level or try a different method of solving a problem they've already solved. The extension is a separate session.
- **On solutions:** they are in `solutions/`. Suggest a student opens one after a real attempt and a hint, looks at the one problem, then closes it and writes the answer themselves.

## Common problems and fixes

| What the student sees | Cause | Fix |
|-----------------------|-------|-----|
| Colab asks them to sign in, or will not save | Colab needs a Google account | Any Google account works, the simplest is to use a personal one. If you're stuck on a work network that blocks Google login, try a different network or your personal device. |
| "Warning: This notebook was not authored by Google" | Colab warns about every notebook opened from GitHub | Choose **Run anyway**. |
| Their work disappears when they close the tab | They worked on the original and not a copy | Lost work cannot be recovered. Reopen from the badge and first select **File > Save a copy in Drive** and redo the work. If the tab is still open, saving a copy now preserves what they have. |
| `ModuleNotFoundError: No module named 'adh_python'` | Setup cell was not run (or runtime was restarted) | Run the setup cell at the top, then carry on. |
| `NameError: name '...' is not defined` | Cells run out of order or skipped or the runtime restarts and forgets prior variables | **Runtime > Run before** (runs every cell above the current cell) or **Runtime > Restart session and run all**. |
| "Runtime disconnected" | Colab stops idle sessions | Reconnect then **Runtime > Run before**. This keeps the notebook text and code but clears any variables. |
| `IndentationError` or `SyntaxError` despite code looking correct | Code pasted from Word, Teams or email, with curly quotes or mixed spaces | Retype the quotes or delete the indent and re-indent with the Tab key. |
| The checker shows ⏳ despite them writing an answer | The `...` is still there / they wrote the answer in a different cell | Replace the `...` itself in the same cell as the checker. |
| MedVision lab: No GPU or "Cannot connect to GPU backend" | Free GPUs in Colab are limited and not always available | Check **Runtime > Change runtime type > T4 GPU**. If none is available, carry on without one: the lab detects this and shows replies recorded earlier with a compressed version of the same model, so every question except trying their own prompts can still be answered. Do not let students wait for a GPU. |
| MedVision lab: the model download is slow or fails | The model (about 8.6 GB) is downloaded from Hugging Face the first time the lab runs; it needs no account or token | Wait for the download or rerun the cell. If it still fails, continue with the saved reference outputs. |
| MedVision lab: "CUDA out of memory" | Another notebook in the same session is using the GPU | **Runtime > Disconnect and delete runtime** then reopen only the lab. |

## The extension session

The extension (`extension/vibe_code_ward_dashboard.ipynb`) is a longer, separate session where students build a small ward dashboard with an AI assistant. They write a specification, have code generated, test it, debug it, and judge the trade-offs. The session plan, timings, and facilitator notes are in [extension/FACILITATOR.md](extension/FACILITATOR.md).

## Reusing the course next year

The notebooks install the course helpers from this repo, and any copies students save keep pointing at it. So treat this repo as the 2026 edition: push bug fixes here, but build the course for the next cohort in a new repo (e.g. `OxfordADH2027PythonBootcamp`) rather than modifying the lessons in this one. For the next run:

- Update dates, cohort name, and module start date in the README and here.
- Change the repository name used in the Colab badges and the setup cell.
- Open every notebook from its badge on a fresh Colab runtime and run it end-to-end, including the MedVision lab on a GPU (the model download is ± 8.6 GB and doesn't require a Hugging Face account).
- Check which AI assistant students are able to use inside Colab for the extension.

## Reporting a problem

If a notebook fails, a checker rejects a correct answer, or something is wrong in the text, please open an issue in this repository (the **Issues** tab on GitHub) or pass it along to the course team. Please include:

- the notebook name and the problem number or cell;
- what you did and what you expected;
- the full error message, copied as text; and
- whether it happened on a GPU or CPU runtime.

Do not include patient information or anything that may identify a student.
