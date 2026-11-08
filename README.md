# Provenance Guard

> ### 👋 Start here
>
> **New to this repo? Read [RUNNING.md](RUNNING.md) first.**
>
> Once `python test.py` passes, in one terminal:
>
> ```bash
> python app.py
> ```
>
> and in another:
>
> ```bash
> curl -X POST http://127.0.0.1:5000/ping \
>   -H "Content-Type: application/json" \
>   -d '{"message": "hello"}'
> ```
>
> That's a web service. Something sent it text and it sent something back.
> Everything this unit is filling in the middle.
>
> **The rest of this file is your submission.** Fill it in as you go.

---

<!-- ─────────────────────────────────────────────────────────────────────────
     Unit 7 asks for the first five sections. Unit 8 adds the five below.

     Everything is pasted as TEXT. A pasted curl response gets full credit;
     a picture of your terminal gets none.
     ───────────────────────────────────────────────────────────────────────── -->

<!-- ═══════════════════════ UNIT 7 — THE BUILD ═══════════════════════ -->

## What This Does

<!-- The path a submission takes, from arriving to the label a reader sees.
     Six or seven steps — this is the trace you wrote in Milestone 1. -->

A submission enters the service through POST /submit as JSON containing text
and creator_id.

1. The route receives the submission and creates a unique content_id.
2. detector.model_signal(text) measures how predictable the writing is to a
   language model and produces model_score. A higher score means more likely AI.
3. stylometry.style_signal(text) measures writing style, including sentence
   length variation, vocabulary repetition, and punctuation. It produces
   style_score. A higher score means more likely AI.
4. scoring.combine_signals(model_score, style_score) combines both scores into
   one combined score.
5. scoring.score_to_label(combined_score) converts the score into a guess and a
   reader-facing label.
6. audit.log_decision(...) records the content_id, creator_id, both signal
   scores, the combined score, label, and status.
7. The service returns the decision as JSON to the caller.

The model signal cannot determine true authorship; it only measures
predictability. The style signal cannot understand the meaning of the text and can be affected by typos, quotations, or sentence changes. Therefore, the
result is an estimate, not proof that a person or AI wrote the submission.

---

## Signals and Scoring

<!-- For each signal: what property it measures, why that might differ between
     human and AI writing, and WHAT IT CAN'T SEE.

     The blind spot is not optional. If you can't name it you don't understand
     the signal yet — and unit 8's attack set is built out of blind spots. -->

### Signal one — the model signal

**What it measures:** detector.py uses a local language model to measure how predictable the submitted text is. It calculates perplexity and converts it into a score from 0 to 1. A higher model_score means the text is more predictable and therefore more AI-like according to this signal.

**Why that might differ between human and AI writing:** AI-generated writing often selects common, statistically likely words and follows predictable sentence patterns. This can make it easier for another language model to predict. Human writing may contain unusual word choices, unexpected transitions, or personal phrasing that is harder for the model to predict.

**What it can't see:** It cannot determine who actually wrote the text. It only measures predictability. Plain, conventional human writing may look AI-like, while formal or unusual AI writing may look human-like. It also cannot understand the writer's intent, effort, sources, or personal authorship.

### Signal two — the style signal

**What it measures:** stylometry.py measures the text's surface patterns rather than its meaning. The three planned measures are sentence-length variation, vocabulary variety using type-token ratio, and punctuation density or variety. These are combined into a style_score from 0 to 1.

**Why that might differ between human and AI writing:** AI writing often has consistent sentence lengths, repeated common vocabulary, and regular punctuation. Human writing may have more variation, such as a short sentence followed by a long one, more uneven word choices, and individualized punctuation habits. These differences can make the writing's shape look more human or more AI-like.

**What it can't see:** It cannot understand what the text means or determine whether the ideas are original. It can be fooled by changing the surface appearance, such as adding typos, splitting or combining sentences, changing punctuation, repeating words, or inserting a quotation without changing the underlying ideas.

### False-positive trace

A real writer submits an original paragraph through POST /submit. The system
runs both signals. Because the writing is predictable and has regular sentence
patterns, the signals produce these example scores:

model_score = 0.78
style_score = 0.62

Using the current 50/50 weights, the combined score is:

(0.78 × 0.5) + (0.62 × 0.5) = 0.70

The combined score is above the current AI threshold of 0.65, so the system
labels the submission as high-confidence AI. The writer sees a message saying
that the work was probably written by AI, even though the writer wrote it
themselves. This is a false positive.

The response includes a content_id. The writer can use that ID to submit an
appeal through POST /appeal with an explanation. The system records the appeal
in the audit log and changes the submission status to under_review while
preserving the original decision.

This scenario shows why the unsure range and AI threshold matter. A predictable
human writing style should not automatically be treated as proof of AI
authorship, so the system should be cautious before giving a strong AI label.

### Endpoint contracts

These are the contracts another client can use without knowing how the service
is implemented.

#### `POST /submit`

**Request body:** JSON object with these fields:

| Field        | Type   | Required | Meaning                                        |
| ------------ | ------ | -------- | ---------------------------------------------- |
| `text`       | string | yes      | The writing to evaluate. It must not be empty. |
| `creator_id` | string | yes      | Identifies the person submitting the writing.  |

**Successful response:** HTTP `200`, JSON object with these fields:

| Field            | Type   | Meaning                                              |
| ---------------- | ------ | ---------------------------------------------------- |
| `content_id`     | string | Unique ID for this submission and future appeals.    |
| `guess`          | string | Machine-readable result: `human`, `unsure`, or `ai`. |
| `confidence`     | number | Confidence score from `0.0` to `1.0`.                |
| `label`          | string | Reader-facing explanation of the result.             |
| `model_score`    | number | Predictability-based score from `detector.py`.       |
| `style_score`    | number | Surface-style score from `stylometry.py`.            |
| `combined_score` | number | Final score produced by combining both signals.      |

The service also writes the decision to the audit log with status `decided`.

**Invalid request:** HTTP `400` with a JSON object containing `error` and
`message`. The service must not score or log a decision for an invalid request.

#### `POST /appeal`

**Request body:** JSON object with these fields:

| Field        | Type   | Required | Meaning                                                |
| ------------ | ------ | -------- | ------------------------------------------------------ |
| `content_id` | string | yes      | ID returned by an earlier `/submit` request.           |
| `reasoning`  | string | yes      | The writer's explanation for challenging the decision. |

**Successful response:** HTTP `200`, JSON object containing:

```json
{
  "content_id": "the-original-id",
  "status": "under_review",
  "message": "Appeal recorded."
}
```

The original decision remains in the append-only audit log, and a new appeal
entry records the writer's reasoning.

**Unknown content ID:** HTTP `404` with a JSON object containing `error` and
`message`. The service must not create an appeal for an ID that does not exist.

### The combining rule

<!-- Write the rule in words, then give the numbers. What happens when the two
     signals disagree? -->

**The rule:** Take a weighted average of the two signals. If the two signals
disagree by a lot, the text can't be labelled AI: the score is capped just
below the AI threshold, so the most it can get is "unsure". One method on its
own is never enough to accuse someone. The cap only works in one direction:
disagreement can stop an AI label, but it never pushes a score toward AI.

**The numbers:** (in `config.py`)

- `WEIGHT_MODEL_SIGNAL = 0.5`, `WEIGHT_STYLE_SIGNAL = 0.5`. The signals count
  equally. Neither one proved more trustworthy in testing, because both are
  fooled by plain writing.
- `DISAGREEMENT_GAP = 0.35`. If `|model_score − style_score| > 0.35`, the
  combined score is capped at `AI_THRESHOLD − 0.01` (0.64).
- `HUMAN_THRESHOLD = 0.35`, `AI_THRESHOLD = 0.65`.

**Calibration run** (four required inputs, plus two extras):

| Input | model | style | combined | Band |
|---|---|---|---|---|
| Clearly AI | 0.8669 | 0.5657 | 0.7163 | AI |
| Clearly human | 0.5011 | 0.0659 | 0.2835 | human |
| Formal human | 0.5727 | 0.3931 | 0.4829 | unsure |
| Lightly-edited AI | 0.6818 | 0.5577 | 0.6198 | unsure |
| Plain human (extra) | 0.8824 | 0.6551 | 0.7688 | **AI: false positive** |
| Split case A (extra) | 0.8493 | 0.3909 | 0.6201 | unsure |

- **Formal human** isn't accused. It lands in unsure, mostly because the style
  signal reads its varied punctuation and sentence lengths as human.
- **Lightly-edited AI** drops from AI to unsure. Simplifying the words was
  enough to pull the model signal down from 0.87 to 0.68.
- **Plain human is the known failure.** Both signals score it *higher* than
  the clearly AI text. Short, predictable words fool the model signal, and
  flat sentence lengths with no punctuation fool the style signal. A combining
  rule can't fix a case where both inputs are wrong in the same direction.
  The fix would have to come from the signals themselves.

**Where it lives:** `scoring.py::combine_signals`

<!-- ⚠️ The grader checks your code against that line. If your rule lives
     somewhere else, say where. -->

**A case where my two signals split, and what my rule does with it:**

I ran both signals over three test pieces:

| Piece | model_score | style_score |
|---|---|---|
| A: clearly AI (generic "AI has transformed modern life…" paragraph) | 0.8493 | 0.3909 |
| B: clearly human (casual, lumpy "missed the bus again" rant) | 0.4953 | 0.0857 |
| C: plain human (flat "went to the store after work" diary entry) | 0.8576 | 0.5873 |

- **Agree:** B. Both signals score it as the most human.
- **Split:** A. The model signal says strongly AI (0.85). The style signal leans
  human (0.39), because a short paragraph has a high type-token ratio (0.84)
  and only moderate sentence spread (0.43).
- **Agree, but wrong:** C. Both signals lean AI on a real human's plain
  writing. The model scores it *higher* than the actual AI text, because
  simple, predictable words read as "likely" text. This is the false-accusation
  case.

My combining rule has to handle A: one signal is confident and the other
isn't. It also has to avoid labelling C as AI.

**What my rule does with A:** the signals are 0.46 apart, which is more than
`DISAGREEMENT_GAP` (0.35). So A can't be labelled AI, and it lands in
**unsure** (0.62). With these numbers the average was already below 0.65, so
the cap didn't change anything. But if the model had said 0.95 against a style
score of 0.40, the plain average (0.675) would have been an accusation. The
cap holds it at 0.64.

---

## Label Variants

<!-- The exact text of all three labels, as a reader would see them, and the
     score range each covers.

     Write them for someone who has never heard the word "threshold". -->

| Label                 | Score range | The exact text a reader sees |
| --------------------- | ----------- | ---------------------------- |
| high-confidence human | 0.00 – 0.35 | "We think this was probably written by a person. Our checks found the kind of variety in wording and sentence length that is typical of human writing." |
| unsure                | above 0.35, below 0.65 | "We can't tell whether this was written by a person or with help from AI. Our checks gave mixed results, which happens often with genuine human writing, especially plain or formal styles. This is not an accusation, and it shouldn't be treated as evidence either way." |
| high-confidence AI    | 0.65 – 1.00 | "We think this was likely written with help from AI. Our checks found patterns common in AI-generated text, such as very predictable wording and evenly sized sentences. These checks can be wrong. If you wrote this yourself, you can appeal, and a person will review it." |

A score of exactly 0.35 counts as human, and exactly 0.65 counts as AI (see
`scoring.py::score_to_label`).

**Why I worded the "unsure" one this way:** The person reading it may well
have written every word themselves. My own testing shows plain human writing
scoring as high as real AI text, so "unsure" has to read as a statement about
*our tool's limits*, not about the writer. That's why it:

- leads with "we can't tell", which puts the uncertainty on us and not on them
- says outright that mixed results are common for real human writing, and
  names plain and formal styles, because those are the writers most likely to
  get this label
- says it is not an accusation or evidence, so a teacher or editor reading it
  doesn't treat it as a soft "AI" label
- never mentions scores, thresholds or confidence numbers, because "0.52" means
  nothing to a writer and sounds more certain than it is

The AI label also stays hedged ("likely", "can be wrong") and points to the
appeal. Even at the high end, this tool has produced false positives.

<!-- It's the hardest of the three. It has to admit uncertainty without
     sounding like an accusation, because the person reading it may well have
     written every word themselves. -->

---

## Sample Run

<!-- One submission and one appeal, pasted as text: the request, the response,
     and the log entries. -->

**A submission**

<!-- The response needs content_id, guess, confidence, label, AND both
     signal scores - model_score and style_score. Unit 8's tools read those
     two off the response, so leaving them out costs you next unit's
     diagnostics. -->

```bash
$ curl.exe -X POST http://127.0.0.1:5000/submit -H "Content-Type: application/json" -d '{\"text\": \"I learned that software decisions should be tested with evidence and recorded clearly.\", \"creator_id\": \"student-1\"}'
```

```json
{
  "confidence": null,
  "content_id": "014a1830-4af4-427c-a5f0-781902bfc16e",
  "creator_id": "student-1",
  "guess": null,
  "label": null,
  "model_score": 0.0603,
  "style_score": null
}
```

**An appeal**

```bash
$ curl -X POST http://127.0.0.1:5000/appeal \
  -H "Content-Type: application/json" \
  -d '{"content_id": "...", "reasoning": "..."}'
```

```json

```

**What the log shows afterwards**

```bash
$ curl.exe "http://127.0.0.1:5000/log?limit=3"
```

```json
{
  "count": 1,
  "entries": [
    {
      "combined_score": null,
      "content_id": "014a1830-4af4-427c-a5f0-781902bfc16e",
      "creator_id": "student-1",
      "guess": null,
      "label": null,
      "model_score": 0.0603,
      "status": "decided",
      "style_score": null,
      "timestamp": "2026-11-05T00:25:11+00:00"
    }
  ]
}
```

---

## How I Used AI

**Moment 1**

- _What I asked for:_
- _What came back:_
- _What I changed:_

**Moment 2**

- _What I asked for:_
- _What came back:_
- _What I changed:_

<!-- ═══════════════════════ UNIT 8 — THE TEST ═══════════════════════ -->

---

## Rate Limiting

**My limits:** **_ per minute, _** per day

**Why those numbers and not others:**

<!-- Think about two people: a real writer submitting their own work a few
     times an hour, and a script sending a thousand variations to map your
     thresholds. Your numbers have to be liveable for the first and hostile to
     the second. -->

**What a caller counts as:** <!-- per address, or per creator_id? They fail
differently — one script can look like a thousand callers, and one household
can look like one. -->

**The run of status codes when I pushed past it:**

<!-- python run_attacks.py --flood 15 -->

```

```

---

## Attack Run — Before

<!-- Every attack with its outcome and a held-or-broke mark.
     `run_attacks.py --label before` produces the table. -->

**Ten audit log entries from the run**

<!-- Choose entries that show the interesting failures, not the ten easiest. -->

```json

```

**The single worst outcome** — the one I'd least want to explain to a writer
whose work got caught by it:

---

## Run Log and Verdicts

<!-- Your five criteria across three trials. `run_eval.py --label before`. -->

| Criterion | Target | Run 1 | Run 2 | Run 3 | Verdict |
| --------- | ------ | ----- | ----- | ----- | ------- |
| 1.        |        |       |       |       |         |
| 2.        |        |       |       |       |         |
| 3.        |        |       |       |       |         |
| 4.        |        |       |       |       |         |
| 5.        |        |       |       |       |         |

**Real output from one trial**, pasted as text, naming the file and function
that produced it:

```json

```

**Diagnoses**

<!-- For each miss AND each broken attack: the stage and the mechanism.

     Your service has five stages: the route, signal one, signal two, the
     combining rule, and the label mapping.

     Not a diagnosis:  "The evasion attacks got through."
     A diagnosis:      "Four evasion inputs got through. All four had typos
                        added to AI-generated text. My second signal measures
                        word variety, and typos raise word variety — so it read
                        them as more human. My combining rule weights that
                        signal at 0.6, so it dragged the whole score down."

     Look for a pattern. Five failures on one signal is one problem, not five. -->

---

## The Improvement

**What I changed:**

**Which diagnosis pointed at it:**

### Attack Run — After

<!-- Same format. `run_attacks.py --label after` -->

**Did it help, and how do I know:**

<!-- Widening the unsure band usually fixes one problem and creates another.
     Reporting that trade honestly is worth full credit. -->

---

## What's Still Broken

<!-- For each attack still getting through and each criterion still missed:
     what you'd do, and why you stopped. -->

**The trade I'd make if this ran for real:**

<!-- Two sentences. Fewer wrong accusations means more AI text getting through.
     Say which way you'd go and WHO PAYS FOR IT. -->

<!-- ═════════════════════════════════════════════════════════════════════

     SUBMISSION CHECKLIST — unit 7

       [ ] criteria.md has five numbered criteria, each naming a target
       [ ] Each has a reason underneath
       [ ] POST /submit returns content_id, guess, confidence, label,
           model_score and style_score
       [ ] Two signals that measure DIFFERENT things, each with a named blind spot
       [ ] Three label variants, all reachable, written out in full
       [ ] POST /appeal changes status and writes to the log
       [ ] Signals and Scoring names scoring.py::combine_signals
       [ ] Sample Run: a submission AND an appeal, as pasted text
       [ ] At least four new commits
       [ ] Repository URL submitted — WRITE IT DOWN

     SUBMISSION CHECKLIST — unit 8

       [ ] Rate limiting on /submit, with your numbers justified
       [ ] The pasted run of status codes showing 429
       [ ] Audit log with all nine fields, recording rejections too
       [ ] The attack set run IN FULL, every input with an outcome
       [ ] Ten audit log entries pasted as text
       [ ] Five criteria across three trials
       [ ] A diagnosis for every miss and every broken attack — stage AND mechanism
       [ ] One improvement, with Attack Run — After
       [ ] What's Still Broken, including the production trade
       [ ] At least four new commits
       [ ] The SAME repository URL as last unit

     Do not delete and recreate this repository.
     ═════════════════════════════════════════════════════════════════════ -->

---

📖 **How to run this project: [RUNNING.md](RUNNING.md)**
