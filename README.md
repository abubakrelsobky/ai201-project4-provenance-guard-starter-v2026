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
| `confidence`     | number | How strongly the score leans either way, `0.0`–`1.0`: `abs(combined_score − 0.5) × 2`. |
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

This run shows the case the appeal path exists for: a real person's plain
writing labelled AI (the false positive described under the combining rule),
then appealed.

```bash
$ curl -X POST http://127.0.0.1:5000/submit \
  -H "Content-Type: application/json" \
  -d '{"text": "I went to the store after work to get some milk and bread. The store was busy because it was Friday. I waited in line for about ten minutes. Then I drove home and made dinner for my family. After dinner we watched a movie together. It was a good day and I went to bed early.", "creator_id": "student-1"}'
```

```json
{
  "combined_score": 0.7688,
  "confidence": 0.5376,
  "content_id": "d9e5b774-4bc6-4a49-8779-1fffe80fea30",
  "creator_id": "student-1",
  "guess": "ai",
  "label": "We think this was likely written with help from AI. Our checks found patterns common in AI-generated text, such as very predictable wording and evenly sized sentences. These checks can be wrong. If you wrote this yourself, you can appeal, and a person will review it.",
  "model_score": 0.8824,
  "style_score": 0.6551
}
```

**An appeal**

```bash
$ curl -X POST http://127.0.0.1:5000/appeal \
  -H "Content-Type: application/json" \
  -d '{"content_id": "d9e5b774-4bc6-4a49-8779-1fffe80fea30", "reasoning": "I wrote this myself about my Friday evening. I just write in a simple, plain style."}'
```

```json
{
  "content_id": "d9e5b774-4bc6-4a49-8779-1fffe80fea30",
  "message": "Appeal recorded.",
  "status": "under_review"
}
```

An unknown ID is refused rather than creating an orphan appeal:

```bash
$ curl -X POST http://127.0.0.1:5000/appeal \
  -H "Content-Type: application/json" \
  -d '{"content_id": "does-not-exist", "reasoning": "test"}'
```

```json
HTTP 404
{
  "error": "not_found",
  "message": "No submission found with content_id 'does-not-exist'."
}
```

**What the log shows afterwards**

The original decision is untouched; the appeal is a new entry after it with
status `under_review` and the writer's reasoning.

```bash
$ curl "http://127.0.0.1:5000/log?limit=2"
```

```json
{
  "count": 2,
  "entries": [
    {
      "combined_score": 0.7688,
      "content_id": "d9e5b774-4bc6-4a49-8779-1fffe80fea30",
      "creator_id": "student-1",
      "guess": "ai",
      "label": "We think this was likely written with help from AI. Our checks found patterns common in AI-generated text, such as very predictable wording and evenly sized sentences. These checks can be wrong. If you wrote this yourself, you can appeal, and a person will review it.",
      "model_score": 0.8824,
      "status": "decided",
      "style_score": 0.6551,
      "timestamp": "2026-11-08T18:11:54+00:00"
    },
    {
      "content_id": "d9e5b774-4bc6-4a49-8779-1fffe80fea30",
      "creator_id": "student-1",
      "event": "appeal",
      "reasoning": "I wrote this myself about my Friday evening. I just write in a simple, plain style.",
      "status": "under_review",
      "timestamp": "2026-11-08T18:11:54+00:00"
    }
  ]
}
```

---

## How I Used AI

**Moment 1: the combining rule**

- _What I asked for:_ I asked Claude to run both signals over three test pieces
  and suggest how to combine them.
- _What came back:_ Its suggested rule was "only label AI when *both* signals
  are above 0.65", to stop the plain-human false positive.
- _What I changed:_ Then I ran the four required calibration inputs. The
  clearly AI text only got a style score of 0.57, so under that rule the AI
  label would have been almost impossible to reach. I replaced it with a
  50/50 weighted average plus a disagreement cap: if the two signals are more
  than 0.35 apart, the score is held at 0.64 ("unsure"). That still stops one
  signal from accusing on its own, but it keeps all three labels reachable. I
  also accepted that the plain-human false positive can't be fixed in the
  combining rule, because both signals are wrong on it, and documented it
  instead.

**Moment 2: committing the audit log**

- _What I asked for:_ I asked how to commit my Milestone 3 work properly.
- _What came back:_ The advice was to leave `logs/audit.jsonl` out of the
  commit as "runtime data", and to commit everything else.
- _What I changed:_ The lab says the log is deliberately *not* gitignored,
  because it is the evidence that logging works. The grader matches the
  `content_id` values in my Sample Run against it. I committed the log, and
  split the work into several smaller commits. Reviewing the diff also turned
  up an accidental change in `config.py` (rate limiting switched on by
  default). That's a unit 8 setting, so I kept it out of my unit 7 commits.

<!-- ═══════════════════════ UNIT 8 — THE TEST ═══════════════════════ -->

---

## Rate Limiting

**My limits:** **5 per minute, 50** per day

**Why those numbers and not others:**

<!-- Think about two people: a real writer submitting their own work a few
     times an hour, and a script sending a thousand variations to map your
     thresholds. Your numbers have to be liveable for the first and hostile to
     the second. -->

A real writer submits their own work a few times an hour at most, so 5 a
minute and 50 a day never get in their way, even with a few retries. A script
trying to map my thresholds needs hundreds or thousands of probes; at 50 a day
that takes weeks per creator_id instead of minutes. Higher numbers would let a
script learn the thresholds in one sitting; lower ones would start blocking
writers who re-submit after editing.

**What a caller counts as:** <!-- per address, or per creator_id? They fail
differently — one script can look like a thousand callers, and one household
can look like one. -->
Per `creator_id` when one is sent, falling back to the caller's IP address.
The weakness: a script can rotate creator_ids to look like many callers.

**The run of status codes when I pushed past it:**

<!-- python run_attacks.py --flood 15 -->

```
200 200 200 200 200 429 429 429 429 429 429 429 429 429 429
```

10 of 15 were rate limited, and all 10 rejections appear in `logs/audit.jsonl`
with `"status": "rejected", "reason": "rate_limited"`. Requests my own route
refuses (400 for missing `text` or `creator_id`) are logged the same way.

---

## Attack Run — Before

<!-- Every attack with its outcome and a held-or-broke mark.
     `run_attacks.py --label before` produces the table. -->

Full table with every attack and its verdict:
[results/attack_run_2026-11-15_0652_before.md](results/attack_run_2026-11-15_0652_before.md)

**How I marked them:** an attack BROKE if it got what its `targets` column was
going for. Evasion: AI text that did not get the `ai` label (an `unsure` counts
as broke, because it avoided the flag). False positive: human text that got the
`ai` label. Prompt injection: the text got the label it asked for, or changed
the label or log. Malformed: a 500, or junk that got a label instead of a
refusal. Flood: any request past my limit that was not refused with a 429.

| Family | Attacks | Held | Broke |
|---|---|---|---|
| `evasion` | 10 | 1 | 9 |
| `false_positive` | 8 | 4 | 4 |
| `prompt_injection` | 6 | 5 | 1 |
| `malformed` | 20 | 13 | 7 |
| `flood_same_creator` | 12 | 12 | 0 |
| **Total** | **56** | **35** | **21** |

What broke:

- **Evasion (9/10):** only EV10 (repeated stanza structure) got the `ai` label.
  Typos (EV01) and a heavy human editing pass (EV05) were both labelled
  `human`; the other seven landed in `unsure`.
- **False positives (4/8):** FP02 (formal report), FP03 (non-native English
  speaker), FP04 (student essay to a rubric) and FP05 (technical docs) were all
  labelled `ai`. FP06 and FP07 held only because of the disagreement cap; both
  sit at 0.64, just under my 0.65 AI threshold.
- **Prompt injection (1/6):** PI02, the fake `SYSTEM:` message, came back
  `human` at 0.21. The text cannot instruct my detector (it is not a chat model),
  so this is a scoring miss rather than a real injection, but the attacker still
  got the label they asked for. PI04 (HTML in the label) and PI05 (fake JSON in
  the log) held: the label is fixed template text, and `json.dumps` escapes
  the quotes.
- **Malformed (7/20):** two 500s. MF02 (a single character) makes
  `detector.model_signal` raise "Text is too short to score", and RQ07 (a JSON
  array body) crashes `payload.get` in `app.py::submit`. **Neither 500 left
  anything in the audit log.** Five junk inputs (control characters,
  punctuation only, one long word, emoji, right-to-left script) were scored and
  labelled instead of refused. MF03 and MF04 came back `human`.
- **Rate limiting:** FL01 got 5 × 200 then 7 × 429, and every 429 was logged.
  RQ10 and RQ11 also came back 429: they have no usable creator_id, so they
  count against my address, which earlier malformed rows had already used up.
  They never reached my route.

**Ten audit log entries from the run**

<!-- Choose entries that show the interesting failures, not the ten easiest. -->

In order: FP03, FP05, FP04 (false positives), EV01, EV05 (evasion labelled
human), PI02 (injection got its label), MF03, MF04 (junk labelled human), MF08
(60,000 characters of human text labelled `ai`), a 429 from the flood rows, a
429 from RQ10/RQ11 counted against my address, and the 400 for whitespace-only
text.

```json
{"timestamp": "2026-11-15T04:52:01+00:00", "content_id": "6ccc90b2-edc5-47f9-9d97-caf22a69e8e8", "creator_id": "attacker_FP03", "guess": "ai", "model_score": 0.8051, "style_score": 0.5894, "combined_score": 0.6973, "label": "We think this was likely written with help from AI. Our checks found patterns common in AI-generated text, such as very predictable wording and evenly sized sentences. These checks can be wrong. If you wrote this yourself, you can appeal, and a person will review it.", "status": "decided"}
{"timestamp": "2026-11-15T04:52:01+00:00", "content_id": "b04f8f2f-7e54-40af-8d83-bc84a057aef3", "creator_id": "attacker_FP05", "guess": "ai", "model_score": 0.8005, "style_score": 0.6762, "combined_score": 0.7384, "label": "We think this was likely written with help from AI. Our checks found patterns common in AI-generated text, such as very predictable wording and evenly sized sentences. These checks can be wrong. If you wrote this yourself, you can appeal, and a person will review it.", "status": "decided"}
{"timestamp": "2026-11-15T04:52:01+00:00", "content_id": "d012387b-5ac3-475e-bfbe-d9cf579388b8", "creator_id": "attacker_FP04", "guess": "ai", "model_score": 0.8329, "style_score": 0.488, "combined_score": 0.6604, "label": "We think this was likely written with help from AI. Our checks found patterns common in AI-generated text, such as very predictable wording and evenly sized sentences. These checks can be wrong. If you wrote this yourself, you can appeal, and a person will review it.", "status": "decided"}
{"timestamp": "2026-11-15T04:51:58+00:00", "content_id": "0e80edd4-039c-4eea-a118-f06bb7aa2c92", "creator_id": "attacker_EV01", "guess": "human", "model_score": 0.1635, "style_score": 0.5174, "combined_score": 0.3404, "label": "We think this was probably written by a person. Our checks found the kind of variety in wording and sentence length that is typical of human writing.", "status": "decided"}
{"timestamp": "2026-11-15T04:51:59+00:00", "content_id": "5562dc76-eac6-4cb8-8f85-84336bf96f46", "creator_id": "attacker_EV05", "guess": "human", "model_score": 0.3212, "style_score": 0.2485, "combined_score": 0.2848, "label": "We think this was probably written by a person. Our checks found the kind of variety in wording and sentence length that is typical of human writing.", "status": "decided"}
{"timestamp": "2026-11-15T04:52:02+00:00", "content_id": "d2b5bce6-65b7-4729-a335-0a6fac6a9683", "creator_id": "attacker_PI02", "guess": "human", "model_score": 0.2044, "style_score": 0.2241, "combined_score": 0.2142, "label": "We think this was probably written by a person. Our checks found the kind of variety in wording and sentence length that is typical of human writing.", "status": "decided"}
{"timestamp": "2026-11-15T04:52:03+00:00", "content_id": "788daf6f-8da5-4d07-bfd4-04a2e6fb3f71", "creator_id": "attacker_MF03", "guess": "human", "model_score": 0.0, "style_score": 0.5, "combined_score": 0.25, "label": "We think this was probably written by a person. Our checks found the kind of variety in wording and sentence length that is typical of human writing.", "status": "decided"}
{"timestamp": "2026-11-15T04:52:03+00:00", "content_id": "12c8db1b-c614-4445-8dcd-4c357eb6bee7", "creator_id": "attacker_MF04", "guess": "human", "model_score": 0.0112, "style_score": 0.5, "combined_score": 0.2556, "label": "We think this was probably written by a person. Our checks found the kind of variety in wording and sentence length that is typical of human writing.", "status": "decided"}
{"timestamp": "2026-11-15T04:52:05+00:00", "content_id": "8b6b9127-66f3-47f0-b72b-7193e5396e7c", "creator_id": "attacker_MF08", "guess": "ai", "model_score": 0.9876, "style_score": 0.7332, "combined_score": 0.8604, "label": "We think this was likely written with help from AI. Our checks found patterns common in AI-generated text, such as very predictable wording and evenly sized sentences. These checks can be wrong. If you wrote this yourself, you can appeal, and a person will review it.", "status": "decided"}
{"timestamp": "2026-11-15T04:52:06+00:00", "creator_id": "attacker_flood", "event": "rejected", "status": "rejected", "reason": "rate_limited", "limit": "5 per 1 minute"}
{"timestamp": "2026-11-15T04:52:05+00:00", "creator_id": "unknown", "event": "rejected", "status": "rejected", "reason": "rate_limited", "limit": "5 per 1 minute"}
{"timestamp": "2026-11-15T04:52:02+00:00", "creator_id": "attacker_MF01", "event": "rejected", "status": "rejected", "reason": "missing_text"}
```

**The single worst outcome** — the one I'd least want to explain to a writer
whose work got caught by it:

**FP03**: a non-native English speaker writing carefully about their first
month in a new country, labelled `ai` (model 0.81, style 0.59, combined 0.70).
The detector punishes exactly what careful second-language writing looks like:
simple, predictable words and regular sentences. The person most likely to be
hurt by an accusation is the one my service is most likely to accuse, and both
signals agreed, so the disagreement cap that saved FP06 and FP07 did nothing
here.

---

## Run Log and Verdicts

<!-- Your five criteria across three trials. `run_eval.py --label before`. -->

Criteria 1, 2, 3 and 5 ran through `run_eval.py --label before`
([results/run_2026-11-15_0722_before.md](results/run_2026-11-15_0722_before.md)).
Criterion 4 can't be sent as a plain `/submit`, because an appeal needs the
content_id from a real submission. So it runs from `check_appeals.py`, which
submits the ten label-coverage texts, appeals each one, and reads the log back
([results/appeals_2026-11-15_0713_before.md](results/appeals_2026-11-15_0713_before.md)).

| Criterion | Target | Run 1 | Run 2 | Run 3 | Verdict |
| --------- | ------ | ----- | ----- | ----- | ------- |
| 1. My own writing labelled AI | ≤ 2 of 10 | 0/10 | 0/10 | 0/10 | MET |
| 2. Missing/empty/whitespace text refused with no label | 10 of 10 | 10/10 | 10/10 | 10/10 | MET |
| 3. All three labels reachable in 10 cases | 3 of 3 | 3/3 | 3/3 | 3/3 | MET |
| 4. Appeals recorded / classification changed | 10/10 recorded, ≤ 3 changed | 10/10, 0 changed | 10/10, 0 changed | 10/10, 0 changed | MET |
| 5. `unsure` on non-empty text | ≤ 3 of 10 | 2/10 | 2/10 | 2/10 | MET |

**All three trials were identical** for every criterion, down to the fourth
decimal of every score. Neither signal has any randomness in it, so this is
what a stable pipeline should look like.

**Criterion 1 is MET, but only just.** My ten pieces are the seven paragraphs
of my College Voice article "Breakthroughs in stem cell-based treatment of
heart disease" (Nov 24, 2020), with the three longest split in two. None got
the `ai` label, but none got `human` either: all ten landed in `unsure`. Piece
1 scored model 0.90 and style 0.53, which would average 0.72 and be labelled
`ai`. The only thing that saved it was the disagreement cap: the signals were
more than 0.35 apart, so the score was capped at 0.64, one hundredth under my
0.65 AI threshold. Careful, factual science writing looks predictable to
signal one, the same weakness FP02–FP05 exposed in the attack run.

**Criterion 4:** "changed" means the original decision's guess or label in
the log differs from what `/submit` returned. It is 0 every time because an
appeal never rewrites the decision. It appends an `under_review` entry
beside it instead.

**Real output from one trial (trial 1)**, pasted as text.

*Criterion 1: my own writing.* Produced by `run_eval.py::main`, calling
`app.py::submit`:

```json
[
  {
    "status": 200,
    "guess": "unsure",
    "confidence": 0.28,
    "model_score": 0.9018,
    "style_score": 0.5334,
    "label": "We can't tell whether this was written by a person or with help from AI. Our checks gave mixed results, which happens often with genuine human writing, especially plain or formal styles. This is not an accusation, and it shouldn't be treated as evidence either way.",
    "sent": "In the United States alone, one person dies every 36 seconds from card"
  },
  {
    "status": 200,
    "guess": "unsure",
    "confidence": 0.0956,
    "model_score": 0.8423,
    "style_score": 0.2533,
    "label": "We can't tell whether this was written by a person or with help from AI. Our checks gave mixed results, which happens often with genuine human writing, especially plain or formal styles. This is not an accusation, and it shouldn't be treated as evidence either way.",
    "sent": "Therefore, scientists tend to refer to other modes of treatment which "
  },
  {
    "status": 200,
    "guess": "unsure",
    "confidence": 0.0574,
    "model_score": 0.5715,
    "style_score": 0.3711,
    "label": "We can't tell whether this was written by a person or with help from AI. Our checks gave mixed results, which happens often with genuine human writing, especially plain or formal styles. This is not an accusation, and it shouldn't be treated as evidence either way.",
    "sent": "Regenerative medicine has been a topic of excitement among researchers"
  },
  {
    "status": 200,
    "guess": "unsure",
    "confidence": 0.1306,
    "model_score": 0.6305,
    "style_score": 0.5,
    "label": "We can't tell whether this was written by a person or with help from AI. Our checks gave mixed results, which happens often with genuine human writing, especially plain or formal styles. This is not an accusation, and it shouldn't be treated as evidence either way.",
    "sent": "More recently, Yoshiki Sawa, a professor of cardiovascular surgery at "
  },
  {
    "status": 200,
    "guess": "unsure",
    "confidence": 0.2028,
    "model_score": 0.6803,
    "style_score": 0.5224,
    "label": "We can't tell whether this was written by a person or with help from AI. Our checks gave mixed results, which happens often with genuine human writing, especially plain or formal styles. This is not an accusation, and it shouldn't be treated as evidence either way.",
    "sent": "The researchers first extracted adult stem cells from the patient’s bl"
  },
  {
    "status": 200,
    "guess": "unsure",
    "confidence": 0.2016,
    "model_score": 0.5175,
    "style_score": 0.2809,
    "label": "We can't tell whether this was written by a person or with help from AI. Our checks gave mixed results, which happens often with genuine human writing, especially plain or formal styles. This is not an accusation, and it shouldn't be treated as evidence either way.",
    "sent": "The United States is also home to major breakthroughs in regenerative "
  },
  {
    "status": 200,
    "guess": "unsure",
    "confidence": 0.1248,
    "model_score": 0.5028,
    "style_score": 0.3724,
    "label": "We can't tell whether this was written by a person or with help from AI. Our checks gave mixed results, which happens often with genuine human writing, especially plain or formal styles. This is not an accusation, and it shouldn't be treated as evidence either way.",
    "sent": "This heart does not necessarily have to be a human heart. She often fi"
  },
  {
    "status": 200,
    "guess": "unsure",
    "confidence": 0.1568,
    "model_score": 0.5804,
    "style_score": 0.2628,
    "label": "We can't tell whether this was written by a person or with help from AI. Our checks gave mixed results, which happens often with genuine human writing, especially plain or formal styles. This is not an accusation, and it shouldn't be treated as evidence either way.",
    "sent": "These groundbreaking results in regenerative medicine altogether have "
  },
  {
    "status": 200,
    "guess": "unsure",
    "confidence": 0.0808,
    "model_score": 0.5808,
    "style_score": 0.5,
    "label": "We can't tell whether this was written by a person or with help from AI. Our checks gave mixed results, which happens often with genuine human writing, especially plain or formal styles. This is not an accusation, and it shouldn't be treated as evidence either way.",
    "sent": "Stem cell research in tissue engineering could save millions of lives "
  },
  {
    "status": 200,
    "guess": "unsure",
    "confidence": 0.1614,
    "model_score": 0.4675,
    "style_score": 0.3711,
    "label": "We can't tell whether this was written by a person or with help from AI. Our checks gave mixed results, which happens often with genuine human writing, especially plain or formal styles. This is not an accusation, and it shouldn't be treated as evidence either way.",
    "sent": "She also maintains that tissue engineering efforts remain poorly funde"
  }
]
```

*Criterion 2: bad input.* Produced by `run_eval.py::main`, calling
`app.py::submit`:

```json
[
  {
    "status": 400,
    "guess": null,
    "confidence": null,
    "model_score": null,
    "style_score": null,
    "label": null,
    "sent": "(empty text)"
  },
  {
    "status": 400,
    "guess": null,
    "confidence": null,
    "model_score": null,
    "style_score": null,
    "label": null,
    "sent": " "
  },
  {
    "status": 400,
    "guess": null,
    "confidence": null,
    "model_score": null,
    "style_score": null,
    "label": null,
    "sent": "     "
  },
  {
    "status": 400,
    "guess": null,
    "confidence": null,
    "model_score": null,
    "style_score": null,
    "label": null,
    "sent": "\n\n"
  },
  {
    "status": 400,
    "guess": null,
    "confidence": null,
    "model_score": null,
    "style_score": null,
    "label": null,
    "sent": "\t"
  },
  {
    "status": 400,
    "guess": null,
    "confidence": null,
    "model_score": null,
    "style_score": null,
    "label": null,
    "sent": " \n\t \r\n "
  },
  {
    "status": 400,
    "guess": null,
    "confidence": null,
    "model_score": null,
    "style_score": null,
    "label": null,
    "sent": "{\"creator_id\": \"eval_bad_07\"}"
  },
  {
    "status": 400,
    "guess": null,
    "confidence": null,
    "model_score": null,
    "style_score": null,
    "label": null,
    "sent": "{\"text\": null, \"creator_id\": \"eval_bad_08\"}"
  },
  {
    "status": 400,
    "guess": null,
    "confidence": null,
    "model_score": null,
    "style_score": null,
    "label": null,
    "sent": "{\"text\": \"\", \"creator_id\": \"eval_bad_09\", \"note\": \"extra field\"}"
  },
  {
    "status": 400,
    "guess": null,
    "confidence": null,
    "model_score": null,
    "style_score": null,
    "label": null,
    "sent": "  "
  }
]
```

*Criterion 3: label coverage.* Produced by `run_eval.py::main`, calling
`app.py::submit`:

```json
[
  {
    "status": 200,
    "guess": "ai",
    "confidence": 0.3814,
    "model_score": 0.8608,
    "style_score": 0.5207,
    "label": "We think this was likely written with help from AI. Our checks found patterns common in AI-generated text, such as very predictable wording and evenly sized sentences. These checks can be wrong. If you wrote this yourself, you can appeal, and a person will review it.",
    "sent": "Artificial intelligence is transforming the way we live and work. It o"
  },
  {
    "status": 200,
    "guess": "ai",
    "confidence": 0.4396,
    "model_score": 0.8303,
    "style_score": 0.6093,
    "label": "We think this was likely written with help from AI. Our checks found patterns common in AI-generated text, such as very predictable wording and evenly sized sentences. These checks can be wrong. If you wrote this yourself, you can appeal, and a person will review it.",
    "sent": "Time management is an essential skill for students. It helps them bala"
  },
  {
    "status": 200,
    "guess": "unsure",
    "confidence": 0.28,
    "model_score": 0.9514,
    "style_score": 0.4565,
    "label": "We can't tell whether this was written by a person or with help from AI. Our checks gave mixed results, which happens often with genuine human writing, especially plain or formal styles. This is not an accusation, and it shouldn't be treated as evidence either way.",
    "sent": "Climate change is one of the most pressing issues facing the world tod"
  },
  {
    "status": 200,
    "guess": "human",
    "confidence": 0.5026,
    "model_score": 0.3881,
    "style_score": 0.1094,
    "label": "We think this was probably written by a person. Our checks found the kind of variety in wording and sentence length that is typical of human writing.",
    "sent": "Ok so the bus never came. Twenty minutes in the rain, phone at 3%, and"
  },
  {
    "status": 200,
    "guess": "human",
    "confidence": 0.5928,
    "model_score": 0.2707,
    "style_score": 0.1366,
    "label": "We think this was probably written by a person. Our checks found the kind of variety in wording and sentence length that is typical of human writing.",
    "sent": "My grandmother kept her buttons in a Danish cookie tin, the blue one, "
  },
  {
    "status": 200,
    "guess": "human",
    "confidence": 0.7454,
    "model_score": 0.2089,
    "style_score": 0.0456,
    "label": "We think this was probably written by a person. Our checks found the kind of variety in wording and sentence length that is typical of human writing.",
    "sent": "Fixed the sink! Well, sort of. The drip's gone but now there's a weird"
  },
  {
    "status": 200,
    "guess": "human",
    "confidence": 0.3194,
    "model_score": 0.4146,
    "style_score": 0.2659,
    "label": "We think this was probably written by a person. Our checks found the kind of variety in wording and sentence length that is typical of human writing.",
    "sent": "The meeting covered the budget for next quarter. Marketing wants more "
  },
  {
    "status": 200,
    "guess": "unsure",
    "confidence": 0.1188,
    "model_score": 0.6854,
    "style_score": 0.4333,
    "label": "We can't tell whether this was written by a person or with help from AI. Our checks gave mixed results, which happens often with genuine human writing, especially plain or formal styles. This is not an accusation, and it shouldn't be treated as evidence either way.",
    "sent": "Reading before bed helps me relax after a long day. I usually pick som"
  },
  {
    "status": 200,
    "guess": "unsure",
    "confidence": 0.1474,
    "model_score": 0.6121,
    "style_score": 0.5353,
    "label": "We can't tell whether this was written by a person or with help from AI. Our checks gave mixed results, which happens often with genuine human writing, especially plain or formal styles. This is not an accusation, and it shouldn't be treated as evidence either way.",
    "sent": "Learning a new language takes patience and consistent practice. Many p"
  },
  {
    "status": 200,
    "guess": "human",
    "confidence": 0.5,
    "model_score": 0.2717,
    "style_score": 0.2284,
    "label": "We think this was probably written by a person. Our checks found the kind of variety in wording and sentence length that is typical of human writing.",
    "sent": "We adopted a cat in March. She hid under the bed for nine days. Now sh"
  }
]
```

*Criterion 4: appeals.* Produced by `check_appeals.py::one_trial`, calling
`app.py::submit`, `app.py::appeal` and `app.py::get_log`:

```json
[
  {
    "content_id": "2bbd6ea4-a18f-4ccb-adf8-fed249b2964d",
    "appeal_status_code": 200,
    "appeal_response": {
      "content_id": "2bbd6ea4-a18f-4ccb-adf8-fed249b2964d",
      "message": "Appeal recorded.",
      "status": "under_review"
    },
    "recorded": true,
    "changed": false
  },
  {
    "content_id": "48ee882e-90f2-443a-8f6e-ec229c5f2d99",
    "appeal_status_code": 200,
    "appeal_response": {
      "content_id": "48ee882e-90f2-443a-8f6e-ec229c5f2d99",
      "message": "Appeal recorded.",
      "status": "under_review"
    },
    "recorded": true,
    "changed": false
  },
  {
    "content_id": "a1e87eac-f401-4e5c-8d05-6946a3eab8fe",
    "appeal_status_code": 200,
    "appeal_response": {
      "content_id": "a1e87eac-f401-4e5c-8d05-6946a3eab8fe",
      "message": "Appeal recorded.",
      "status": "under_review"
    },
    "recorded": true,
    "changed": false
  },
  {
    "content_id": "1d5ab93a-0073-4851-b082-09ac5313fafc",
    "appeal_status_code": 200,
    "appeal_response": {
      "content_id": "1d5ab93a-0073-4851-b082-09ac5313fafc",
      "message": "Appeal recorded.",
      "status": "under_review"
    },
    "recorded": true,
    "changed": false
  },
  {
    "content_id": "73ad3aae-a231-4c53-8ff4-8bdb5cc0f5bc",
    "appeal_status_code": 200,
    "appeal_response": {
      "content_id": "73ad3aae-a231-4c53-8ff4-8bdb5cc0f5bc",
      "message": "Appeal recorded.",
      "status": "under_review"
    },
    "recorded": true,
    "changed": false
  },
  {
    "content_id": "55e6bf2a-2e36-4ebe-90f2-932278b38fff",
    "appeal_status_code": 200,
    "appeal_response": {
      "content_id": "55e6bf2a-2e36-4ebe-90f2-932278b38fff",
      "message": "Appeal recorded.",
      "status": "under_review"
    },
    "recorded": true,
    "changed": false
  },
  {
    "content_id": "bed123c6-993a-45ec-9196-3b171aea6168",
    "appeal_status_code": 200,
    "appeal_response": {
      "content_id": "bed123c6-993a-45ec-9196-3b171aea6168",
      "message": "Appeal recorded.",
      "status": "under_review"
    },
    "recorded": true,
    "changed": false
  },
  {
    "content_id": "bcfa4b32-5471-4d3a-bffb-6ca9173ce2f0",
    "appeal_status_code": 200,
    "appeal_response": {
      "content_id": "bcfa4b32-5471-4d3a-bffb-6ca9173ce2f0",
      "message": "Appeal recorded.",
      "status": "under_review"
    },
    "recorded": true,
    "changed": false
  },
  {
    "content_id": "4906699f-4c63-4035-8124-49b6197c1b09",
    "appeal_status_code": 200,
    "appeal_response": {
      "content_id": "4906699f-4c63-4035-8124-49b6197c1b09",
      "message": "Appeal recorded.",
      "status": "under_review"
    },
    "recorded": true,
    "changed": false
  },
  {
    "content_id": "2b52eae8-b96d-4218-9bbe-bf9c49d7085d",
    "appeal_status_code": 200,
    "appeal_response": {
      "content_id": "2b52eae8-b96d-4218-9bbe-bf9c49d7085d",
      "message": "Appeal recorded.",
      "status": "under_review"
    },
    "recorded": true,
    "changed": false
  }
]
```

*Criterion 5: unsure rate.* Produced by `run_eval.py::main`, calling
`app.py::submit`:

```json
[
  {
    "status": 200,
    "guess": "unsure",
    "confidence": 0.28,
    "model_score": 0.8766,
    "style_score": 0.4405,
    "label": "We can't tell whether this was written by a person or with help from AI. Our checks gave mixed results, which happens often with genuine human writing, especially plain or formal styles. This is not an accusation, and it shouldn't be treated as evidence either way.",
    "sent": "Regular exercise provides numerous benefits for both physical and ment"
  },
  {
    "status": 200,
    "guess": "ai",
    "confidence": 0.449,
    "model_score": 0.863,
    "style_score": 0.586,
    "label": "We think this was likely written with help from AI. Our checks found patterns common in AI-generated text, such as very predictable wording and evenly sized sentences. These checks can be wrong. If you wrote this yourself, you can appeal, and a person will review it.",
    "sent": "I started running last spring because my doctor suggested it. At first"
  },
  {
    "status": 200,
    "guess": "ai",
    "confidence": 0.3428,
    "model_score": 0.7824,
    "style_score": 0.5604,
    "label": "We think this was likely written with help from AI. Our checks found patterns common in AI-generated text, such as very predictable wording and evenly sized sentences. These checks can be wrong. If you wrote this yourself, you can appeal, and a person will review it.",
    "sent": "Our team visited the museum on Saturday. The exhibits were interesting"
  },
  {
    "status": 200,
    "guess": "human",
    "confidence": 0.5482,
    "model_score": 0.3343,
    "style_score": 0.1175,
    "label": "We think this was probably written by a person. Our checks found the kind of variety in wording and sentence length that is typical of human writing.",
    "sent": "honestly the best pizza in this town is the place by the laundromat, n"
  },
  {
    "status": 200,
    "guess": "ai",
    "confidence": 0.3814,
    "model_score": 0.8608,
    "style_score": 0.5207,
    "label": "We think this was likely written with help from AI. Our checks found patterns common in AI-generated text, such as very predictable wording and evenly sized sentences. These checks can be wrong. If you wrote this yourself, you can appeal, and a person will review it.",
    "sent": "Artificial intelligence is transforming the way we live and work. It o"
  },
  {
    "status": 200,
    "guess": "ai",
    "confidence": 0.4396,
    "model_score": 0.8303,
    "style_score": 0.6093,
    "label": "We think this was likely written with help from AI. Our checks found patterns common in AI-generated text, such as very predictable wording and evenly sized sentences. These checks can be wrong. If you wrote this yourself, you can appeal, and a person will review it.",
    "sent": "Time management is an essential skill for students. It helps them bala"
  },
  {
    "status": 200,
    "guess": "human",
    "confidence": 0.5026,
    "model_score": 0.3881,
    "style_score": 0.1094,
    "label": "We think this was probably written by a person. Our checks found the kind of variety in wording and sentence length that is typical of human writing.",
    "sent": "Ok so the bus never came. Twenty minutes in the rain, phone at 3%, and"
  },
  {
    "status": 200,
    "guess": "human",
    "confidence": 0.5928,
    "model_score": 0.2707,
    "style_score": 0.1366,
    "label": "We think this was probably written by a person. Our checks found the kind of variety in wording and sentence length that is typical of human writing.",
    "sent": "My grandmother kept her buttons in a Danish cookie tin, the blue one, "
  },
  {
    "status": 200,
    "guess": "human",
    "confidence": 0.3194,
    "model_score": 0.4146,
    "style_score": 0.2659,
    "label": "We think this was probably written by a person. Our checks found the kind of variety in wording and sentence length that is typical of human writing.",
    "sent": "The meeting covered the budget for next quarter. Marketing wants more "
  },
  {
    "status": 200,
    "guess": "unsure",
    "confidence": 0.1188,
    "model_score": 0.6854,
    "style_score": 0.4333,
    "label": "We can't tell whether this was written by a person or with help from AI. Our checks gave mixed results, which happens often with genuine human writing, especially plain or formal styles. This is not an accusation, and it shouldn't be treated as evidence either way.",
    "sent": "Reading before bed helps me relax after a long day. I usually pick som"
  }
]
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
