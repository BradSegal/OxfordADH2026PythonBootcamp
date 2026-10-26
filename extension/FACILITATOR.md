# Facilitator notes: vibe coding a ward early-warning dashboard

Notebook: `extension/vibe_code_ward_dashboard.ipynb` (worked answers in
`extension/solutions/`).

## What the session is for

Students have asked to be taught "vibe coding". This is an area without a settled evidence base for best practice, and so the session does not claim to have one. Rather, it teaches a disciplined loop: **specify, generate, test, debug, judge**. The core lesson is one students already know from clinical practice: define what right looks like before you look at the result.

The project is a NEWS2 ward dashboard on the synthetic ward `data.ward(seed=2026)` and three patients "admitted tonight" (`check.new_admissions`). These are the same three patients every time, and they carry the lesson:

| Patient        | Why they are there                                                        |
|----------------|---------------------------------------------------------------------------|
| Margaret Ellis | Newly confused, total 7, high. The unfixed draft shows her as 4, low.     |
| Arjun Mehta    | Pneumonia, total 7, high. With his respiration rate missing, A shows 4, low. |
| Graham Price   | COPD on SpO2 scale 2, total 5, medium. Code that ignores the scale says 8, high. |

Attempt A calls both totals of 7 medium. The notebook refers to these patients by name, with their bed numbers following on from the generated ward.

Students define the scoring function as test cases and get an AI assistant to write the function. They then test the output and adjudicate two frozen 'AI' attempts. All expected answers are derived from `adh_python.clinical`.

**Prerequisites:** Levels 1 to 6 (dicts, lists of dicts, `.get`, `None`, functions, raising `ValueError`). Levels 7 and 8 help but aren't needed.

**AI access is optional.** Nothing in the notebook depends on live AI output. A student with no assistant writes the prompt anyway, debugs the frozen draft, and uses it in place of their own generated code.

## Before the session

- Open the student notebook from its Colab badge on a fresh runtime and run all cells once. It should complete without errors (incomplete problems will show ⏳ or ❌; this is to be expected).
- Decide which assistant the students can leverage. The simplest is to use Colab's Gemini panel, however, it may not be available for all accounts / regions. A browser tab with any assistant works. Pair students up to ensure at least one assistant is available per pair.
- Say the information governance rule out loud at the start: the data is invented, and never paste real patient data into an assistant unless the organisation has approved that tool for that data.

## Running it as a 75-minute session

| Time      | Phase              | What happens                                                                                              |
|-----------|--------------------|-----------------------------------------------------------------------------------------------------------|
| 0:00-0:05 | Introduction       | Frame vibe coding honestly: fast, plausible, sometimes wrong. Show the loop. State the IG rule.           |
| 0:05-0:10 | How NEWS2 works    | Walk through the chart, the three steps and the worked example. Stress the band edges, scale 2 and the single-3 rule. |
| 0:10-0:15 | 1 Specify, E.1     | Plain-English requirements. Ask two pairs to read theirs aloud; point out what they left out.            |
| 0:15-0:25 | 1 Specify, E.2     | Test cases. This is the slowest step. Circulate; most help needed is on expected values.                 |
| 0:25-0:35 | 2 Generate, E.3    | Prompt card, write the prompt, send it. While waiting for this, students read the assistant's tests compared to their own. |
| 0:35-0:45 | 3 Debug, E.4       | Run the draft first and look at Margaret Ellis on the dashboard then fix it. Everyone does this.        |
| 0:45-0:50 | 3 Test, E.5        | Paste and test their own assistant's code; run the course suite. Cut first when short of time.          |
| 0:50-1:02 | 4 Judge, E.6-E.7   | Read A and B, predict, compare dashboards, run tests, find A's second bug.                               |
| 1:02-1:10 | 4 Judge, E.8       | Whole room discussion on the trade-offs (prompts below) then each pair records a decision.             |
| 1:10-1:15 | 5 Reflect          | Start the reflection questions; finish after the session.                                                |

**If you are short of time:** cut E.5 for everyone in a live session (students can do it afterwards) and redirect the time to Phase 4; skip the stretch case for E.2; run E.3 once on the projector with a shared assistant; and set the reflection as follow-up work. Do not cut E.4 or E.6: these carry the main lessons. For E.4, ensure they run the draft and look at the dashboard before fixing it; otherwise they never see Margaret Ellis shown as low.

**Self-paced:** The notebook is self-contained. Suggested times are indicated by the phase headings. A solutions notebook is provided with worked solutions and example model reflections.

## Common sticking points

- **Forgetting `.copy()`.** `edge = well_patient` and then modifying `edge` modifies the well patient, so the first test now fails its own check ("you expect total 0, the RCP chart gives 2"). Ask: "what does `=` do to a dict?"
- **The shape of `"expected"`.** Students write `"error"`, `ValueError` (without quotes), `"Low"` or `"low medium"`. The checker names the accepted forms: a dictionary with `"total"` and `"risk"`, or the string `"ValueError"`.
- **Consciousness as a word.** `"confused"` instead of `"C"`. Checker asks for an ACVPU letter as per the ward data.
- **E.1 and E.3 checkers are checklists.** They look only for key words and accept standard alternatives (missing, absent, null, incomplete, not recorded; error, exception, refuse, reject). If an answer is complete but not recognised by either checker, it is still complete: advise the student to move on.
- **Working out expected values.** Few students have all the NEWS2 bands memorised and some have never worked with the chart. Point them to the chart in "How NEWS2 is calculated", then to the single-parameter reference functions, e.g. `clinical.score_respiration_rate(21)`. The checker also prints the per-parameter scores if the total is incorrect.
- **Scale 2 arithmetic.** SpO2 89% on oxygen on scale 2 scores 0 for SpO2 (within target) plus 2 for oxygen, a total of 2. Many students forget the oxygen points or apply scale 1.
- **Pasting into E.5.** If you paste the code above `score_news2 = ...` and don't remove that line, it will overwrite the function with `...` and the runner will show ⏳. Just delete the line.
- **Assistant output that doesn't match the tests.** A different function name (rename it), a tuple `(total, risk)` instead of a dict (the runner explains this), `print` instead of `return` (the runner reports `None`), example calls at the bottom with their own data, or `input()` calls that make the cell wait for typing. Delete anything after the function.
- **Running cells out of order.** A `NameError` for `score_news2_a` or `my_tests` implies an earlier cell hasn't been run. Use Runtime, then "Run before".

## Discussion prompts for Phase 4

- Attempt A is about a quarter the length of B. Who finds it easier to check against the RCP chart, and why?
- A's `if obs.get(name) is not None` was probably intended to be helpful. When is "skip what is missing" a reasonable design, and why is it not here?
- Arjun Mehta with no respiration rate: A shows low, B shows "cannot score". Which would you rather see at 3 in the morning? What actually happens next on the ward in each case?
- Both attempts copy the chart; the draft calls tested functions instead. If the RCP were to revise a band, how many things need to change in each?
- The person who generated this code rotates in four months. What does the person who inherits it need?
- Most trusts will already calculate NEWS2 within an electronic observations system. What would justify building a second?
- What would have to be true before this went anywhere near a real ward?

## Answer key

### E.1 and E.2

Model requirements and test cases are included in the solutions notebook. The expected values for the suggested cases are:

| Case                                         | Expected                         |
|----------------------------------------------|----------------------------------|
| Respiration rate not recorded                | `"ValueError"`                   |
| Respiration rate 21 (edge between 0 and 2)   | total 2, low                     |
| Scale 2, SpO2 89% on oxygen                  | total 2, low (0 for SpO2, 2 for oxygen) |
| New confusion, otherwise well                | total 3, low-medium (a single 3) |
| Stretch: RR 25, pulse 115, SpO2 93           | total 7, high                    |

### E.4: the draft

**Bug:** `if observations["consciousness"] in ["V", "P", "U"]` is missing `"C"`. This is the original NEWS chart (AVPU); NEWS2 added new confusion, with the same score as V, P and U. Without the fix, Margaret Ellis (newly confused, true total 7, high) is displayed on the dashboard as 4, low, and every other newly confused patient on the ward is under-scored by 3.

**Fix:** `consciousness_score = clinical.score_consciousness(observations["consciousness"])`. Adding `"C"` to the list also passes. Point out that the one rule the draft wrote for itself, instead of calling the tested owner, is the one that was wrong.

### E.6: prediction

Attempt A reports a value of **4** for Arjun Mehta with the missing respiratory rate: SpO2 93% (2) + Pulse 116 (2) with all other values 0 as well as the missing respiratory rate being skipped. The true value based on his recorded respiratory rate of 25 (3 points) is 7 which is high. This demonstrates a patient that would trigger emergency response to be flagged as low risk.

### Attempt A: two bugs

1. **Missing observations are scored as normal.** Three places do it:
   - `if obs.get(name) is not None` in the list comprehension skips any
     missing numeric observation;
   - `2 * bool(obs.get("on_oxygen"))` treats missing oxygen status as air;
   - `(obs.get("consciousness") or "A")` treats missing consciousness as
     alert.

   The course suite shows all 8 missing-observation cases failing.
2. **Boundary bug:** `"high" if total > 7` should be `total >= 7`. A total of
   exactly 7 is reported as medium: Margaret Ellis and Arjun Mehta tonight.
   The course suite shows the two "Total 7" cases failing.

A passes 68 of the 78 course tests. Its thresholds are otherwise correct.

### Attempt B

B passes all 78 course tests and raises a `ValueError` that names the missing observation. The test runner checks for this, if you raise a `ValueError` that does not name the missing observation (e.g. `ValueError("bad data")`) the test will fail as someone reading it will not know what to re-measure. Some reasonable caveats that are worth teasing out are:

- Every threshold is restated in its own helper functions, so if the chart is revised you edit B, and there is nothing anchoring B to a tested owner.
- It is stricter than the reference in two ways. The reference only allows the letters A, C, V, P, and U but is case and space insensitive (`" c "` would be considered a C); B only matches the exact capital letter. B also rejects any SpO2 value outside 0 to 100, which the reference does not check. Both raise a `ValueError` if given a word like `"alert"`. This is arguably right for dashboard use.
- Does not check other values are plausible (a pulse of 0 is scored)
- A missing `spo2_scale` silently implies scale 1. If the patient is on scale 2 this will over-score rather than under-score, which is the safer direction, but it is still a silent default and worth calling out.

**Model decision:** build on B as it is correct on all tests and fails loudly. Before any use, replace its copied thresholds with calls to a single tested owner and add plausibility checks. Neither attempt is ready for a ward.

The E.8 checker records the choice instead of marking it. It requests a reason of at least eight words that draws on the evidence (tests, failing loudly or silently, readability, maintenance) and indicates which of these it drew on. For A, it names the two bugs that must be fixed first unless the reason already does; for B, it asks about the copied thresholds unless they are mentioned. A pair that selects A with a plan to fix both bugs has made a defensible decision; discuss it rather than correct it.

## Clinical safety and governance: the facts to state

Keep this short and accurate for the session:

- **DCB0129** (Clinical Risk Management: its Application in the Manufacture of Health IT Systems) applies to whoever manufactures a health IT system. **DCB0160** (Clinical Risk Management: its Application in the Deployment and Use of Health IT Systems) applies to the health or care organisation that deploys and uses it. Both are mandatory information standards in England under section 250 of the Health and Social Care Act 2012.
- Both require a clinical risk management process led by a named **Clinical Safety Officer** (a registered clinician with the appropriate clinical safety training), a **hazard log**, and a **clinical safety case report**.
- An organisation that builds a tool in-house is both the manufacturer under DCB0129 and the deployer under DCB0160, and as such is bound by both standards. This is an organisational duty and not the responsibility of the individual who wrote the code.
- Software that calculates a score to inform the care of a patient **may** be a medical device regulated by the MHRA; this is dependent on the intended purpose of the software. Do not tell students that it definitely is or is not.
- Real observations are patient data under UK GDPR and as such require information governance approval for where the code is run and where the data is sent (including any AI tool that has access to it), typically including a data protection impact assessment.
- Scotland, Wales, and Northern Ireland have their own individual processes, the DCB standards are for England.
