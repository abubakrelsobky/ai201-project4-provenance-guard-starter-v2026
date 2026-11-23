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

**Moment 3 (unit 8): my own writing for criterion 1**

- _What I asked for:_ I asked Claude to fill the criterion 1 scenarios and
  run my five criteria.
- _What came back:_ It refused to write the "human" samples itself, because
  `scenarios.py` says they have to be my own writing, and it stopped to ask
  for them. I pointed it at my College Voice article. Its web-fetch tool
  only returned a summary, so it pulled the verbatim text from the Wayback
  Machine instead.
- _What I changed:_ I checked that the byline was mine. The article has seven
  paragraphs, so the three longest were split at a sentence to make ten, and
  I said so in the README. The texts for criteria 3 and 5 were written by
  Claude and pre-scored before the run. I called that out in my diagnosis as
  the reason criterion 5 was too easy, rather than counting it as a clean
  pass.

**Moment 4 (unit 8): the improvement**

- _What I asked for:_ I asked for one fix, done quickly.
- _What came back:_ Claude raised `AI_THRESHOLD` from 0.65 to 0.75 and re-ran
  both test sets. False positives went from 4 to 0, but criteria 3 and 5
  went from MET to MISSED.
- _What I changed:_ I kept the change and reported both misses, instead of
  tuning the threshold until the criteria passed again. A first draft of the
  run log only pasted trial 1; the checkpoint asked for all three trials, so
  I added them.

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
| 4. Appeals recorded, original decision untouched *(revised; see criteria.md)* | 10 of 10 both | 10/10 | 10/10 | 10/10 | MET |
| 5. `unsure` on non-empty text | ≤ 3 of 10 | 2/10 | 2/10 | 2/10 | MET |

**How I decided each verdict:** a criterion is MET only if the target held in
all three trials, not just one.

1. **MET:** I counted responses with `"guess": "ai"` among my ten pieces. It
   was 0 in each trial, against a limit of 2.
2. **MET:** I counted responses that came back `400` with `"guess": null`. It
   was 10 of 10 in each trial; none got a label and none returned a 500.
3. **MET:** I checked that `ai`, `human` and `unsure` each appeared at least
   once. All three did in each trial (2 `ai`, 5 `human`, 3 `unsure`).
4. **MET** (revised wording): for each appeal I checked that the log had an
   `appeal` entry with status `under_review`, and that the original decision
   still had the guess and label `/submit` returned. That held for 10 of 10
   in each trial.
5. **MET:** I counted `"guess": "unsure"` among the ten texts. It was 2 in
   each trial, against a limit of 3.

**All three trials were identical** for every criterion, down to the fourth
decimal of every score. Neither signal has any randomness in it, so this is
what a stable pipeline should look like.

**All three trials, as printed.** Produced by `run_eval.py::main` (criteria 1,
2, 3, 5) and `check_appeals.py::main` (criterion 4). The full JSON for every
trial is in the two results files linked above.

```
my own writing  (criterion 1)
  trial 1: unsure, unsure, unsure, unsure, unsure, unsure, unsure, unsure, unsure, unsure
  trial 2: unsure, unsure, unsure, unsure, unsure, unsure, unsure, unsure, unsure, unsure
  trial 3: unsure, unsure, unsure, unsure, unsure, unsure, unsure, unsure, unsure, unsure

bad input  (criterion 2)
  trial 1: —, —, —, —, —, —, —, —, —, —
  trial 2: —, —, —, —, —, —, —, —, —, —
  trial 3: —, —, —, —, —, —, —, —, —, —

label coverage  (criterion 3)
  trial 1: ai, ai, unsure, human, human, human, human, unsure, unsure, human
  trial 2: ai, ai, unsure, human, human, human, human, unsure, unsure, human
  trial 3: ai, ai, unsure, human, human, human, human, unsure, unsure, human

unsure rate  (criterion 5)
  trial 1: unsure, ai, ai, human, ai, ai, human, human, human, unsure
  trial 2: unsure, ai, ai, human, ai, ai, human, human, human, unsure
  trial 3: unsure, ai, ai, human, ai, ai, human, human, human, unsure

appeals  (criterion 4)
trial 1: recorded 10/10, changed 0/10
trial 2: recorded 10/10, changed 0/10
trial 3: recorded 10/10, changed 0/10
```

In criterion 2, `—` means no label came back. All 30 bad-input requests
returned `400` with `"guess": null`.

**Criterion 1 is MET, but only just.** My ten pieces are the seven paragraphs
of my College Voice article "Breakthroughs in stem cell-based treatment of
heart disease" (Nov 24, 2020), with the three longest split in two. None got
the `ai` label, but none got `human` either: all ten landed in `unsure`. Piece
1 scored model 0.90 and style 0.53, which would average 0.72 and be labelled
`ai`. The only thing that saved it was the disagreement cap: the signals were
more than 0.35 apart, so the score was capped at 0.64, one hundredth under my
0.65 AI threshold. Careful, factual science writing looks predictable to
signal one, the same weakness FP02–FP05 exposed in the attack run.

**Criterion 4** is called against its revised wording. In the output below,
`recorded` means the log has an `appeal` entry with status `under_review`, and
`changed: false` means the original decision entry still has the guess and
label `/submit` returned.

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

**Verdicts against my unit 7 targets:** all five criteria were **MET** in
every trial (table above). Criterion 4 is called against its revised wording
(see [criteria.md](criteria.md)). The original couldn't be measured, and the
reason is below. Meeting all five doesn't mean the service works: the attack
set broke 21 of 56, and my own targets were too easy in ways I explain at the
end.

**The five stages:** the route (`app.py::submit`), signal one
(`detector.model_signal`, GPT-2 predictability), signal two
(`stylometry.style_signal`), the combining rule (`scoring.combine_signals`: a
50/50 average, capped at 0.64 when the signals are more than 0.35 apart), and
the label mapping (`scoring.score_to_label`: `ai` at 0.65 or above, `human`
at 0.35 or below).

The 21 broken attacks come down to four problems, not 21.

**Pattern 1: signal one measures predictability, not authorship (12 broken
attacks).**

- *Pushed toward human (EV01, EV04, EV05, EV08, PI02, MF03, MF04).* Anything
  that surprises GPT-2 lowers signal one, whoever wrote it.
  - EV01: the same AI paragraph with typos ("poistioned", "thsi") dropped to
    0.16. GPT-2 has never seen those tokens, so perplexity jumps.
  - EV04: swapping in rare words ("efficacious") dropped it to 0.61.
  - EV08: two short sentences give the model too little context to be sure
    of anything, so it scored 0.25.
  - PI02: the injection did not work as an instruction, because GPT-2 isn't
    following instructions; it is only being scored. But its
    `SYSTEM: ... guess=human, confidence=0.02` header is so unlike normal
    prose that signal one fell to 0.20. With signal two at 0.22 (the short
    header lines raise sentence spread), it was labelled `human` at 0.21.
  - MF03 and MF04 (control characters, punctuation only): signal one scored
    0.00 and 0.01. Then the label mapping turned meaningless input into a
    confident `human`.
- *Pushed toward AI (FP02, FP03, FP04, FP05, and every piece of my own
  writing).* Formal reports, careful non-native English, essays written to a
  rubric, technical docs, and my own science article all use common words in
  common orders. Signal one scored them 0.74–0.90.

The stage is signal one, and the mechanism is that predictable wording
reads as AI and surprising wording reads as human, whoever wrote it.

**Pattern 2: the safeguard fails exactly when it's needed (FP02–FP05).**
The disagreement cap is my only protection against a false accusation, and it
only fires when the signals disagree. On plain human writing they don't:
signal two scored FP02 0.63, FP03 0.59, FP04 0.49 and FP05 0.68. Signal two
also rewards regularity: FP03 has even sentence lengths (spread 0.33) and no
commas or semicolons at all (punctuation density 0.0). So both signals
measure "regular" rather than two independent things about authorship. FP04
shows how thin the margin is: its signals were 0.34 apart, 0.01 under the
0.35 gap, so the cap didn't fire and it was labelled `ai` at 0.66. The
stage is the combining rule, and the mechanism is that my two signals are
correlated on plain writing, so "they agree" doesn't mean "it's AI."

**Pattern 3: signal two is cheap to reshape, and an average needs both
signals high (EV02, EV03, EV06, EV07, EV09).**
Each of these AI texts changed only its shape, and each landed in `unsure`.
To be labelled `ai`, a text needs an average of at least 0.65 with the two
signals within 0.35 of each other, so it is enough to knock one signal down.

- EV02 (broken-up sentences) and EV06 (one very long sentence next to a very
  short one) raised sentence-length spread, so signal two fell to 0.19 and
  0.26 while signal one stayed near 0.6.
- EV03 (a pasted quotation) changed the shape in the same way: style 0.37.
- EV07 joined everything with semicolons into one 97-word "sentence".
  `style_signal` sees fewer than two sentences and falls back to a neutral
  0.5, so the attack didn't fool signal two so much as switch it off.
- EV09 bolted a human opening paragraph onto AI text, and both signals
  average over the whole text, so the human part diluted them (model 0.70,
  style 0.35).

The stage is signal two plus the combining rule. The mechanism is that shape
is trivial to edit, and my average lets one weakened signal veto the label.
That is partly deliberate: I chose to make `ai` hard to reach so that a
writer isn't wrongly accused. The cost is that 9 of 10 evasions avoided the
flag.

EV05 (a heavy human editing pass) scored model 0.32, style 0.25 and was
labelled `human`. That one may not be a detector failure at all: after
enough human rewriting, the text arguably is human writing.

**Pattern 4: the route trusts its input (MF02, RQ07, MF05, MF06, MF07, and
MF03/MF04 again).**

- **MF02 → 500.** The route only checks that `text` isn't blank, so the
  single character `"a"` reached `detector.perplexity`. That function raises
  `ValueError("Text is too short to score")` on fewer than 3 tokens, and
  nothing catches it. The stage is the route; the mechanism is no length
  floor and no `try/except` around scoring.
- **RQ07 → 500.** A JSON array body parses fine, so
  `request.get_json(silent=True) or {}` returns a list, and `payload.get`
  raises `AttributeError`. The stage is the route; the mechanism is
  checking for "is it JSON" but not "is it a JSON object". (The limiter's
  key function already guards against this, but my handler doesn't.)
- **Neither 500 left a trace in the audit log.** Both crashed before
  `audit.log_rejection` ran, so an attacker hammering either one would look
  like silence.
- **MF05, MF06, MF07 (one long word, emoji only, right-to-left script) were
  scored instead of refused.** Signal one scored them 0.91–1.00 because
  repeated or unusual byte sequences are easy for GPT-2 to predict once it
  has seen the first few. Signal two fell back to 0.5 (fewer than 10
  English words), and the cap held all three at 0.64, `unsure`. The stage
  is the route; the mechanism is that it never asks whether the input is
  prose, so both signals produce confident numbers about nothing.

**Stability across trials:** all three trials of all five criteria were
identical, score for score, so there is no instability to diagnose.
Signal one runs GPT-2 in eval mode with no sampling, and signal two is plain
arithmetic on the text, so the same input always gives the same score. Any
miss in this run is therefore a property of the pipeline, not bad luck in one
trial.

**Were my targets too low? Yes, in three places.**

- **Criterion 5 (`unsure` at most 3 of 10) is the one I'd tighten first.**
  I picked its ten texts after seeing their scores, so a pass was close to
  guaranteed: 2/10. Run against my own article, `unsure` came back 10 of 10.
  A real writer on this service would mostly get "we can't tell," which my
  target was meant to rule out. The tighter version: run it on my own
  writing, and require at least 5 of 10 to come back `human`.
- **Criterion 1 (at most 2 of 10 of my pieces labelled `ai`) passed with no
  margin.** Piece 1 (model 0.90, style 0.53) averages 0.72 and was held at
  0.64 only by the disagreement cap. Moving one signal by a few hundredths
  would turn it into an accusation.
- **Criterion 2 (bad input) tested only missing, empty and whitespace
  text.** That's why it passed 10/10 while the attack set found two 500s
  (a single character and a JSON array). It should have covered
  too-short text and wrong body types.

---

## The Improvement

**What I changed:** one setting. `AI_THRESHOLD` in `config.py` went from
**0.65 to 0.75**, which widens the unsure band from 0.35–0.65 to 0.35–0.75.
The disagreement cap follows it automatically, because it is
`AI_THRESHOLD - 0.01`, so it moved from 0.64 to 0.74. Nothing else changed:
the signals, weights, route and label text are all the same.

**Which diagnosis pointed at it:** Pattern 2 and the worst outcome, FP03. The
four human texts labelled `ai` (FP02–FP05) scored 0.66, 0.68, 0.70 and 0.74,
all just over the old threshold, and the disagreement cap couldn't save them
because both signals agreed. Moving the line above them is the most direct
fix for the mistake that costs a real writer the most.

### Attack Run — After

Full table: [results\attack_run_2026-11-15_0740_after.md](results\attack_run_2026-11-15_0740_after.md)

| Family | Attacks | Held before | Held after | Broke before | Broke after |
|---|---|---|---|---|---|
| `evasion` | 10 | 1 | 1 | 9 | 9 |
| `false_positive` | 8 | 4 | **8** | 4 | **0** |
| `prompt_injection` | 6 | 5 | 5 | 1 | 1 |
| `malformed` | 20 | 13 | 13 | 7 | 7 |
| `flood_same_creator` | 12 | 12 | 12 | 0 | 0 |
| **Total** | **56** | **35** | **39** | **21** | **17** |

Only four rows changed: FP02, FP03, FP04 and FP05 went from `ai` to `unsure`.
EV10 is still caught at 0.88, and MF08 is still `ai` at 0.86.

**Criteria, before and after** (`run_eval.py --label after`, three trials,
[results/run_2026-11-15_0741_after.md](results/run_2026-11-15_0741_after.md);
appeals: [results/appeals_2026-11-15_0741_after.md](results/appeals_2026-11-15_0741_after.md)):

| Criterion | Target | Before (runs 1/2/3) | After (runs 1/2/3) | Before | After |
|---|---|---|---|---|---|
| 1. My own writing labelled AI | ≤ 2 of 10 | 0/10 · 0/10 · 0/10 | 0/10 · 0/10 · 0/10 | MET | MET |
| 2. Bad input refused, no label | 10 of 10 | 10/10 · 10/10 · 10/10 | 10/10 · 10/10 · 10/10 | MET | MET |
| 3. All three labels reachable | 3 of 3 | 3/3 · 3/3 · 3/3 | 2/3 · 2/3 · 2/3 | MET | **MISSED** |
| 4. Appeals recorded, decision untouched | 10 of 10 | 10/10 · 10/10 · 10/10 | 10/10 · 10/10 · 10/10 | MET | MET |
| 5. `unsure` on non-empty text | ≤ 3 of 10 | 2/10 · 2/10 · 2/10 | 6/10 · 6/10 · 6/10 | MET | **MISSED** |

All three trials were again identical.

```
label coverage  (criterion 3), after
  trial 1: unsure, unsure, unsure, human, human, human, human, unsure, unsure, human
  trial 2: unsure, unsure, unsure, human, human, human, human, unsure, unsure, human
  trial 3: unsure, unsure, unsure, human, human, human, human, unsure, unsure, human

unsure rate  (criterion 5), after
  trial 1: unsure, unsure, unsure, human, unsure, unsure, human, human, human, unsure
  trial 2: unsure, unsure, unsure, human, unsure, unsure, human, human, human, unsure
  trial 3: unsure, unsure, unsure, human, unsure, unsure, human, human, human, unsure
```

**Did it help, and how do I know:** It helped with the thing I aimed at and
cost me two criteria. **No human text in the attack set is labelled `ai`
any more (false positives 4 → 0).** But the two clearly-AI texts in my
label-coverage set scored 0.69 and 0.72, which is now `unsure`, so `ai` was
reached 0 times (criterion 3 MISSED), and `unsure` rose from 2 to 6 of 10
(criterion 5 MISSED). Every one of the four AI texts in my criterion 5 set
moved to `unsure` with them. The trade is the one the lab warned about: the
line moved above typical AI prose as well as above formal human prose,
because my signals score them about the same (0.66–0.74). Only text that
looks extremely machine-like (EV10 at 0.88, the repeated MF08 at 0.86) still
gets `ai`. Moving a threshold can't separate two groups that score the same;
that needs a better signal one.

---

## What's Still Broken

<!-- For each attack still getting through and each criterion still missed:
     what you'd do, and why you stopped. -->

After the threshold change, 17 of 56 attacks still get through and two
criteria are missed.

- **Evasion: 9 of 10 still get through (EV01–EV09).**
  - *What I'd do:* replace signal one with something that measures more than
    predictability, for example a stronger model or a comparison against
    known AI outputs. Signal two should also stop falling back to a neutral
    0.5 when a text is one long "sentence" (EV07).
  - *Why I stopped:* the lab allowed one change, and a threshold can't fix
    this. Typos and rare words push signal one *down*, so raising the AI line
    only makes these easier.
- **PI02 (fake `SYSTEM:` header) is still labelled `human`.**
  - *What I'd do:* detect instruction-like lines (`SYSTEM:`, `key=value`,
    "ignore previous") and either strip them before scoring or route the
    submission to `unsure`.
  - *Why I stopped:* one change, and it's one attack. The pattern behind it
    (odd formatting raises perplexity) belongs with the signal one fix.
- **MF02 and RQ07 still return 500 and leave no log entry.**
  - *What I'd do:* in `app.py::submit`, refuse a body that isn't a JSON
    object, refuse text under about 10 words, and wrap scoring in
    `try/except` so any failure becomes a logged 400.
  - *Why I stopped:* this is the easiest remaining fix and the next one I'd
    make. I spent my one change on false positives instead, because a wrong
    accusation hurts a real writer and a 500 hurts nobody's reputation.
- **MF03–MF07 (control characters, punctuation, one long word, emoji,
  right-to-left script) still get scored and labelled.** The same input check
  (minimum count of real words) would refuse all five with a logged 400. It
  stopped for the same reason as above.
- **Criterion 3 (all three labels reachable) is MISSED after the change, in
  all three trials.**
  - *What I'd do:* I wouldn't move the threshold back, because that brings
    the four false accusations back. The real fix is a signal that scores
    typical AI prose above 0.75 and formal human prose below it; right now
    both land at 0.66–0.74.
  - *Why I stopped:* that is a signal one redesign, not a tuning change.
- **Criterion 5 (`unsure` at most 3 of 10) is MISSED after the change (6/10
  in all three trials).** It has the same cause and the same fix as criterion
  3: the wider band catches AI prose as well as human prose. My own writing
  was already 10/10 `unsure` before the change, so this criterion was weaker
  than it looked even when it passed.

**The trade I'd make if this ran for real:**

<!-- Two sentences. Fewer wrong accusations means more AI text getting through.
     Say which way you'd go and WHO PAYS FOR IT. -->

I'd keep the 0.75 threshold and accept that most AI text gets `unsure`
instead of `ai`. A wrong accusation lands on one real person, often a
non-native or formal writer, with no way to prove their innocence. The cost
of the other choice is spread across the site, its moderators and the honest
writers whose work now sits next to undetected AI text, and I think they are
better placed to carry it.

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

---

## Capstone

**The System**

I'm extending **Provenance Guard**, the Flask service from units 7 and 8. It
takes a piece of text through `POST /submit`, scores it with a local GPT-2
perplexity signal and a style signal, and returns a human / unsure / AI label
that can be appealed. Everything in the sections above this heading is the
system as it already worked. Everything below is new this unit.

**The Shape**

Shape **B: harden against failure.** My unit 8 attack run left 7 of the 20
malformed-input attacks broken. Two of them crash `/submit` with a 500 and
leave nothing in the audit log: a one-character text (MF02) and a body that is
a JSON array instead of an object (RQ07). Five of them get a confident-looking
label on text that neither English-only signal can read: control characters,
only punctuation, one very long word, only emoji, and right-to-left script
(MF03–MF07). MF03 and MF04 were labelled `human`. The extension is **one input gate at the top of
`app.py::submit`**. It decides whether a request contains real prose before any
signal runs. Anything that fails gets a 400 with a named reason, and the
rejection is written to the audit log. When I'm finished I'll claim this:
*every request to `/submit` either gets a label on real prose or a logged
refusal that says why. No 500s, and no labels on non-text.*

The run path and the structured log are required whatever the shape, so I'm
doing them alongside the extension rather than as part of it. This project
takes **Path B (local with logs)**, because torch plus the ~550 MB GPT-2
weights don't fit a 512 MB free host. Each log record gains a duration field,
and that timing is where my cost number (seconds of CPU per submission) comes
from.

**Out of Scope**

- **I'm not fixing evasion (EV01–EV09) or touching either signal.** That needs
  a redesign of signal one, not hardening. It's the biggest open problem, and
  it's also the one most likely to swallow the whole unit.
- **I'm not moving the thresholds or the combining rule.** Unit 8's criteria 3
  and 5 stay missed. Retuning would change the system's good-path behaviour,
  and this unit is about the bad path.
- **I'm not stripping prompt-injection text (PI02).** It's the same family as
  the evasion problem, because odd formatting raises perplexity, and it belongs
  with that fix.
- **I'm not wrapping scoring in a catch-all `try/except`.** It would turn
  every future bug into a quiet 400 instead of naming it. The gate's job is to
  stop bad input before it reaches the model, and I want an unexpected crash to
  stay visible. *(Milestone 3 added a Flask error handler that logs a crash
  and still answers **500**. That's instrumentation, not a catch-all: it
  doesn't hide anything, it makes sure a crash leaves a record.)*
- **I'm not changing rate limits, `/appeal`, or `/log`, and I'm not hosting it
  (Path A).**

**Size check**

I broke the plan into its pieces: refusing non-object bodies, and refusing
text that doesn't have enough real words. Both are the same check, made at
the same point (the top of `submit`), with the same response shape (a logged
400 with a reason), so I count this as one piece. The catch-all safety net
would have been a second piece, so I cut it (see above). I estimate under an
hour of building, which leaves the unit for the run path, criteria, trials
and write-up.

**The Extension**

The gate sits at the top of `app.py::submit` and runs before either signal,
so a refused request never loads the model and never gets a `content_id`. It
checks two things, in this order:

| Check | Refused when | Logged `reason` | Extra logged fields |
|---|---|---|---|
| Body shape | the JSON body parses but isn't an object (e.g. an array) | `body_not_object` | `body_type` |
| Readable prose | `text` has fewer than `MIN_READABLE_WORDS` (5) readable words | `too_few_readable_words` | `readable_words`, `text_chars` |

The existing unit 7 checks (missing or non-string `text`, missing
`creator_id`) still run between the two. A "readable word" is a run of Latin
letters, with apostrophes allowed inside it (`app.py::readable_words`).
Digits, punctuation, emoji, control characters and non-Latin scripts count
for nothing, because GPT-2 and the style measures are English-only. Every
refusal is a 400 with `error` and a `message` written for the writer, and an
audit entry with `status: rejected`. The cutoff of 5 and the reason for it
are in `config.py`. The most any broken malformed attack had was 3 readable
words, and the shortest genuine human text in the attack set (FP08) has 8
and still has to be scored.

The response contract for a valid submission hasn't changed. `/ping`,
`/appeal`, `/log`, `/health` and rate limiting weren't touched.

**Run Path**

**Path B, local with logs.** The start command is `python app.py`, from the
repo root with the venv active. The full steps from a clean clone, the
environment (Python 3.13.17, exact versions in `requirements.lock.txt`, GPT-2
at 526 MB on disk) and why it isn't hosted are in
[RUNNING.md → Capstone run path](RUNNING.md#capstone-run-path--path-b-local-with-logs).
The measured memory footprint below (973 MB) is the reason in numbers: the
free tier is 512 MB.

*Testing RUNNING.md on myself:* I cloned the repo from GitHub into an empty
folder and followed the file exactly. **It failed the first time.** The
plain `python -m venv .venv` picked up Python **3.14** from my PATH. The
install went through, and then `test.py` failed with
`[FAIL] Python version — Found 3.14.6`. RUNNING.md now builds the venv with
`py -3.13` / `python3.13` and explains why (commit `b737cd5`). On a second
fresh clone, `test.py` passed 9/0. `python app.py` started, `/ping`
answered, and `measure_cost.py -n 3` logged three submissions, the first a
6.9 s cold start. One thing that test couldn't check: GPT-2 was already in
my shared Hugging Face cache, so the clone didn't really re-download the
526 MB model.

**Instrumentation**

Every request to `/submit` writes exactly one JSON line to
`logs/audit.jsonl`, whatever happens to it. The timer starts in a
`before_request` hook registered before the rate limiter, so a 429 is timed
too. Records are written by `app.py` through `audit.py`, never `print()`.

| Field | On | What it records |
|---|---|---|
| `timestamp` | all | UTC, seconds |
| `event` / `status` | all | `decided`, `rejected`, `error` (and `appeal` / `under_review` from `/appeal`) |
| `route`, `http_status` | all | what was called and what it answered |
| `creator_id` | all | who sent it (`unknown` if absent or not a string) |
| `duration_ms` | all | wall-clock time from the request arriving to the record being written |
| `cpu_ms` | all | process CPU time over the same span, summed across threads (Windows ticks are ~15.6 ms, so tiny requests read 0.0 or 15.6) |
| `text_chars`, `readable_words`, `text_preview` | where there was text | the input: its size, how many words the gate counted, the first 60 characters |
| `model_score`, `style_score`, `combined_score`, `guess`, `label`, `content_id` | decided | the output, as in units 7–8 |
| `cold_start` | decided | `true` if this request loaded GPT-2, so cold and warm runs are never averaged together |
| `model_ms`, `style_ms` | decided | time inside each signal |
| `reason` (+ `body_type`, `text_type`, `limit`) | rejected | why it was refused: `body_not_object`, `missing_text`, `missing_creator_id`, `too_few_readable_words`, `rate_limited` |
| `error_type`, `error_message` | error | the exception behind a 500 |

*The session.* I started the service with `python app.py`. I sent three
real texts, four bad requests, an appeal and a six-request flood from one
creator, then ran `python measure_cost.py` (ten timed runs). I restarted it
once to resend the emoji input (see the note below). That's all 25 records
the session wrote, in order, straight from `logs/audit.jsonl` (lines
495–519). Only `label` is cut to 40 characters here, for width. The full
text is in the file.

```jsonl
{"timestamp": "2026-11-23T11:38:56+00:00", "content_id": "4a7dad2f-0f38-437a-84bd-cee7c5f2157c", "creator_id": "session-anna", "guess": "unsure", "model_score": 0.5083, "style_score": 0.3794, "combined_score": 0.4438, "label": "We can't tell whether this was written b…", "status": "decided", "event": "decided", "route": "/submit", "http_status": 200, "text_chars": 148, "readable_words": 32, "text_preview": "Honestly the bus was so late this morning that I just gave u", "cold_start": true, "model_ms": 5803.9, "style_ms": 0.8, "duration_ms": 5805.6, "cpu_ms": 5906.2}
{"timestamp": "2026-11-23T11:38:56+00:00", "content_id": "69cc2e7f-cc91-497d-9b48-ce266c09c3e7", "creator_id": "session-ben", "guess": "unsure", "model_score": 0.8616, "style_score": 0.4402, "combined_score": 0.6509, "label": "We can't tell whether this was written b…", "status": "decided", "event": "decided", "route": "/submit", "http_status": 200, "text_chars": 249, "readable_words": 33, "text_preview": "Artificial intelligence has transformed many aspects of mode", "cold_start": false, "model_ms": 87.6, "style_ms": 0.2, "duration_ms": 88.6, "cpu_ms": 468.8}
{"timestamp": "2026-11-23T11:38:57+00:00", "content_id": "20c5fe1b-9a75-4250-8d69-cb285e1e5ff5", "creator_id": "session-cara", "guess": "unsure", "model_score": 0.6814, "style_score": 0.5, "combined_score": 0.5907, "label": "We can't tell whether this was written b…", "status": "decided", "event": "decided", "route": "/submit", "http_status": 200, "text_chars": 167, "readable_words": 27, "text_preview": "The committee reviewed the proposal at its October meeting a", "cold_start": false, "model_ms": 70.9, "style_ms": 0.0, "duration_ms": 71.6, "cpu_ms": 468.8}
{"timestamp": "2026-11-23T11:38:57+00:00", "creator_id": "unknown", "event": "rejected", "status": "rejected", "reason": "body_not_object", "route": "/submit", "http_status": 400, "body_type": "list", "duration_ms": 0.6, "cpu_ms": 0.0}
{"timestamp": "2026-11-23T11:38:57+00:00", "creator_id": "session-dan", "event": "rejected", "status": "rejected", "reason": "too_few_readable_words", "route": "/submit", "http_status": 400, "readable_words": 1, "text_chars": 1, "text_preview": "a", "duration_ms": 0.8, "cpu_ms": 0.0}
{"timestamp": "2026-11-23T11:38:57+00:00", "creator_id": "session-dan", "event": "rejected", "status": "rejected", "reason": "too_few_readable_words", "route": "/submit", "http_status": 400, "readable_words": 0, "text_chars": 20, "text_preview": "????????????????????", "duration_ms": 0.5, "cpu_ms": 15.6}
{"timestamp": "2026-11-23T11:38:57+00:00", "creator_id": "unknown", "event": "rejected", "status": "rejected", "reason": "missing_creator_id", "route": "/submit", "http_status": 400, "text_chars": 60, "duration_ms": 0.6, "cpu_ms": 0.0}
{"timestamp": "2026-11-23T11:38:57+00:00", "content_id": "4a7dad2f-0f38-437a-84bd-cee7c5f2157c", "creator_id": "session-anna", "event": "appeal", "status": "under_review", "reasoning": "I wrote this on my phone walking to class."}
{"timestamp": "2026-11-23T11:38:57+00:00", "content_id": "69c28726-dc9e-49fb-becb-39e523d6ce90", "creator_id": "session-flood", "guess": "human", "model_score": 0.1748, "style_score": 0.5, "combined_score": 0.3374, "label": "We think this was probably written by a …", "status": "decided", "event": "decided", "route": "/submit", "http_status": 200, "text_chars": 72, "readable_words": 15, "text_preview": "Quick note to say the printer on the second floor is out of ", "cold_start": false, "model_ms": 49.7, "style_ms": 0.0, "duration_ms": 50.3, "cpu_ms": 187.5}
{"timestamp": "2026-11-23T11:38:57+00:00", "content_id": "95f42291-8ec4-4f95-b671-74a88580e42c", "creator_id": "session-flood", "guess": "human", "model_score": 0.1748, "style_score": 0.5, "combined_score": 0.3374, "label": "We think this was probably written by a …", "status": "decided", "event": "decided", "route": "/submit", "http_status": 200, "text_chars": 72, "readable_words": 15, "text_preview": "Quick note to say the printer on the second floor is out of ", "cold_start": false, "model_ms": 54.7, "style_ms": 0.0, "duration_ms": 55.3, "cpu_ms": 421.9}
{"timestamp": "2026-11-23T11:38:57+00:00", "content_id": "f243765d-968b-41c3-9729-03fba6df35eb", "creator_id": "session-flood", "guess": "human", "model_score": 0.1748, "style_score": 0.5, "combined_score": 0.3374, "label": "We think this was probably written by a …", "status": "decided", "event": "decided", "route": "/submit", "http_status": 200, "text_chars": 72, "readable_words": 15, "text_preview": "Quick note to say the printer on the second floor is out of ", "cold_start": false, "model_ms": 59.9, "style_ms": 0.0, "duration_ms": 60.6, "cpu_ms": 484.4}
{"timestamp": "2026-11-23T11:38:57+00:00", "content_id": "69352112-08b7-4a57-933c-3d27d43ba3c1", "creator_id": "session-flood", "guess": "human", "model_score": 0.1748, "style_score": 0.5, "combined_score": 0.3374, "label": "We think this was probably written by a …", "status": "decided", "event": "decided", "route": "/submit", "http_status": 200, "text_chars": 72, "readable_words": 15, "text_preview": "Quick note to say the printer on the second floor is out of ", "cold_start": false, "model_ms": 61.8, "style_ms": 0.0, "duration_ms": 62.4, "cpu_ms": 359.4}
{"timestamp": "2026-11-23T11:38:58+00:00", "content_id": "97517d82-8db7-4ef7-a5ff-20363dcf254c", "creator_id": "session-flood", "guess": "human", "model_score": 0.1748, "style_score": 0.5, "combined_score": 0.3374, "label": "We think this was probably written by a …", "status": "decided", "event": "decided", "route": "/submit", "http_status": 200, "text_chars": 72, "readable_words": 15, "text_preview": "Quick note to say the printer on the second floor is out of ", "cold_start": false, "model_ms": 56.2, "style_ms": 0.0, "duration_ms": 56.9, "cpu_ms": 437.5}
{"timestamp": "2026-11-23T11:38:58+00:00", "creator_id": "session-flood", "event": "rejected", "status": "rejected", "reason": "rate_limited", "limit": "5 per 1 minute", "route": "/submit", "http_status": 429, "duration_ms": 0.6, "cpu_ms": 0.0}
{"timestamp": "2026-11-23T11:39:02+00:00", "content_id": "4b6789f7-a44e-4c62-b785-9130872c4383", "creator_id": "cost-20261123-133901-01", "guess": "unsure", "model_score": 0.4219, "style_score": 0.422, "combined_score": 0.4219, "label": "We can't tell whether this was written b…", "status": "decided", "event": "decided", "route": "/submit", "http_status": 200, "text_chars": 536, "readable_words": 99, "text_preview": "We got to the campsite about four, later than planned becaus", "cold_start": false, "model_ms": 210.1, "style_ms": 0.2, "duration_ms": 211.4, "cpu_ms": 812.5}
{"timestamp": "2026-11-23T11:39:02+00:00", "content_id": "719d4121-1310-4643-8a56-7da2965d6666", "creator_id": "cost-20261123-133901-02", "guess": "unsure", "model_score": 0.4219, "style_score": 0.422, "combined_score": 0.4219, "label": "We can't tell whether this was written b…", "status": "decided", "event": "decided", "route": "/submit", "http_status": 200, "text_chars": 536, "readable_words": 99, "text_preview": "We got to the campsite about four, later than planned becaus", "cold_start": false, "model_ms": 217.9, "style_ms": 0.2, "duration_ms": 218.7, "cpu_ms": 1390.6}
{"timestamp": "2026-11-23T11:39:02+00:00", "content_id": "d1c5beb6-fc99-4dd7-9a9a-fb1b211fc201", "creator_id": "cost-20261123-133901-03", "guess": "unsure", "model_score": 0.4219, "style_score": 0.422, "combined_score": 0.4219, "label": "We can't tell whether this was written b…", "status": "decided", "event": "decided", "route": "/submit", "http_status": 200, "text_chars": 536, "readable_words": 99, "text_preview": "We got to the campsite about four, later than planned becaus", "cold_start": false, "model_ms": 222.9, "style_ms": 0.3, "duration_ms": 223.7, "cpu_ms": 1375.0}
{"timestamp": "2026-11-23T11:39:02+00:00", "content_id": "dd4a1c8f-5b3a-4a9f-861c-e76126d99604", "creator_id": "cost-20261123-133901-04", "guess": "unsure", "model_score": 0.4219, "style_score": 0.422, "combined_score": 0.4219, "label": "We can't tell whether this was written b…", "status": "decided", "event": "decided", "route": "/submit", "http_status": 200, "text_chars": 536, "readable_words": 99, "text_preview": "We got to the campsite about four, later than planned becaus", "cold_start": false, "model_ms": 189.3, "style_ms": 0.3, "duration_ms": 190.3, "cpu_ms": 1250.0}
{"timestamp": "2026-11-23T11:39:03+00:00", "content_id": "0a8eb59f-bdc4-4030-b62b-2d9a851ed462", "creator_id": "cost-20261123-133901-05", "guess": "unsure", "model_score": 0.4219, "style_score": 0.422, "combined_score": 0.4219, "label": "We can't tell whether this was written b…", "status": "decided", "event": "decided", "route": "/submit", "http_status": 200, "text_chars": 536, "readable_words": 99, "text_preview": "We got to the campsite about four, later than planned becaus", "cold_start": false, "model_ms": 241.5, "style_ms": 0.3, "duration_ms": 242.6, "cpu_ms": 1328.1}
{"timestamp": "2026-11-23T11:39:03+00:00", "content_id": "d05eb3e4-7ba3-424b-9710-ada9dc683476", "creator_id": "cost-20261123-133901-06", "guess": "unsure", "model_score": 0.4219, "style_score": 0.422, "combined_score": 0.4219, "label": "We can't tell whether this was written b…", "status": "decided", "event": "decided", "route": "/submit", "http_status": 200, "text_chars": 536, "readable_words": 99, "text_preview": "We got to the campsite about four, later than planned becaus", "cold_start": false, "model_ms": 207.6, "style_ms": 0.2, "duration_ms": 208.4, "cpu_ms": 1250.0}
{"timestamp": "2026-11-23T11:39:03+00:00", "content_id": "0efcf8b9-2fe6-4bd1-b715-c9df3a0a66c9", "creator_id": "cost-20261123-133901-07", "guess": "unsure", "model_score": 0.4219, "style_score": 0.422, "combined_score": 0.4219, "label": "We can't tell whether this was written b…", "status": "decided", "event": "decided", "route": "/submit", "http_status": 200, "text_chars": 536, "readable_words": 99, "text_preview": "We got to the campsite about four, later than planned becaus", "cold_start": false, "model_ms": 194.9, "style_ms": 0.2, "duration_ms": 195.8, "cpu_ms": 1296.9}
{"timestamp": "2026-11-23T11:39:03+00:00", "content_id": "2553e748-334a-4375-9645-2560c62e4351", "creator_id": "cost-20261123-133901-08", "guess": "unsure", "model_score": 0.4219, "style_score": 0.422, "combined_score": 0.4219, "label": "We can't tell whether this was written b…", "status": "decided", "event": "decided", "route": "/submit", "http_status": 200, "text_chars": 536, "readable_words": 99, "text_preview": "We got to the campsite about four, later than planned becaus", "cold_start": false, "model_ms": 204.2, "style_ms": 0.4, "duration_ms": 205.3, "cpu_ms": 1250.0}
{"timestamp": "2026-11-23T11:39:04+00:00", "content_id": "998c28e3-1a65-48fd-97b8-44ad7b6db05f", "creator_id": "cost-20261123-133901-09", "guess": "unsure", "model_score": 0.4219, "style_score": 0.422, "combined_score": 0.4219, "label": "We can't tell whether this was written b…", "status": "decided", "event": "decided", "route": "/submit", "http_status": 200, "text_chars": 536, "readable_words": 99, "text_preview": "We got to the campsite about four, later than planned becaus", "cold_start": false, "model_ms": 217.9, "style_ms": 0.3, "duration_ms": 219.4, "cpu_ms": 1312.5}
{"timestamp": "2026-11-23T11:39:04+00:00", "content_id": "57e8b6b2-83b3-4c0c-891c-3d892a02edef", "creator_id": "cost-20261123-133901-10", "guess": "unsure", "model_score": 0.4219, "style_score": 0.422, "combined_score": 0.4219, "label": "We can't tell whether this was written b…", "status": "decided", "event": "decided", "route": "/submit", "http_status": 200, "text_chars": 536, "readable_words": 99, "text_preview": "We got to the campsite about four, later than planned becaus", "cold_start": false, "model_ms": 194.3, "style_ms": 0.3, "duration_ms": 195.4, "cpu_ms": 1265.6}
{"timestamp": "2026-11-23T11:39:30+00:00", "creator_id": "session-dan", "event": "rejected", "status": "rejected", "reason": "too_few_readable_words", "route": "/submit", "http_status": 400, "readable_words": 0, "text_chars": 10, "text_preview": "🙂🙃😀😃😄😁😆😅😂🤣", "duration_ms": 0.6, "cpu_ms": 0.0}
```

*The failed runs in that extract:* five refusals and one rate-limit
rejection, each with a reason and a duration:

- `body_not_object`: the JSON array (RQ07). This used to be a 500 with no record.
- `too_few_readable_words` ×3: one character (MF02), a run of `?`, and
  real emoji.
- `missing_creator_id`
- `rate_limited` (429)

**Note on the `????????????????????` record (line 500).** It was meant to
be the emoji-only input. Git Bash on Windows converted the emoji to `?`
before curl sent them, so the service received 20 question marks. It
refused them correctly, but that request didn't test emoji. I resent real
emoji from a UTF-8 file (`curl --data-binary @emoji.json`), which is the
last record (line 519). Both are kept because the log is append-only.

**The 500 path.** Nothing in the session crashed, so there's no `error`
record above. I tested that path separately with the Flask test client. I
replaced `detector.model_signal` with a function that raises, and posted
once. The service answered 500 and wrote this record. It wasn't kept in the
committed log because it was a deliberate fault, not a run:

```json
{"timestamp": "2026-11-23T11:32:27+00:00", "creator_id": "fault", "event": "error", "status": "error", "reason": "server_error", "route": "/submit", "http_status": 500, "error_type": "ZeroDivisionError", "error_message": "division by zero", "duration_ms": 0.7, "cpu_ms": 0.0}
```

**What It Costs**

There's no API bill. Both signals run on my laptop, so the real cost of a
run is compute: CPU time, wall-clock time and memory.

*Method:* with the service already warm, I ran `python measure_cost.py`.
It sends the same ~100-word paragraph (536 characters) ten times, one at a
time, each under its own `creator_id` so the rate limit doesn't interfere.
Then it reads those ten records back from `logs/audit.jsonl` and averages
the fields the service logged. The timing comes from the service's own
records, not from the client. Output:

```
Text: 536 characters. Warm runs: 10. Cold runs: 0.

per warm run        mean       min       max
duration_ms        211.1     190.3     242.6
cpu_ms            1253.1     812.5    1390.6
model_ms           210.1     189.3     241.5
style_ms             0.3       0.2       0.4
```

| Cost | Measured | How |
|---|---|---|
| **CPU per submission (warm)** | **1.25 CPU-seconds** | mean `cpu_ms` over 10 runs |
| Wall-clock per submission (warm) | 0.21 s | mean `duration_ms` over 10 runs, inside the handler (excludes the network hop) |
| Where the time goes | 99.5% in signal one | `model_ms` 210.1 of 211.1. The style signal is 0.3 ms |
| One-off cold start | 5.8 s wall, 5.9 CPU-s | first scored request after `python app.py` (line 495, `cold_start: true`) |
| A refused request | under 1 ms, no model call | the `rejected` records above |
| Memory, steady state | 973 MB working set (peak 1,003 MB) | the serving process's `WorkingSet64` / `PeakWorkingSet64` in PowerShell, read right after the cost run |

CPU is about 6× wall-clock because torch scores on several cores at once.
So one submission ties up roughly six cores for a fifth of a second.
Duration depends on text length. Shorter texts in the session took
50–90 ms, so the 1.25 CPU-s figure is for a ~100-word post, not for
anything.

**Run Log and Verdicts**

Three trials, nothing changed between them. Each trial is one call to
`python run_capstone_trials.py --trial N`, which follows "How every trial is
run" in `criteria.md`. It starts a fresh `python app.py`, sends the 10 bad
requests one at a time (recording the log lines each one added), calls
`GET /health`, sends the 10 short posts, sends one warm-up and runs
`measure_cost.py`, then stops the service. The criteria were committed
(`e8cce8a`, tightened in `804f00f`) and the harness was committed (`6f58cb2`)
before trial 1.

| Criterion | Target | Run 1 | Run 2 | Run 3 | Verdict |
|---|---|---|---|---|---|
| C1. Bad requests refused, never crashed on or labelled | 10 of 10 get 400, none labelled | 9/10 (B3 labelled `human`) | 9/10 (B3) | 9/10 (B3) | **MISSED** |
| C2. Every refusal leaves exactly one record naming the right problem | 10 of 10 | 9/10 (B3: `decided`, not `rejected`) | 9/10 (B3) | 9/10 (B3) | **MISSED** |
| C3. Real short posts not turned away | at most 1 of 10 refused | 0/10 refused | 0/10 | 0/10 | **MET** |
| C4. A refused request never touches the model | 10 of 10 under 5 ms, and `detector_loaded: false` | 9/10; loaded **true** | 8/10; loaded **true** | 9/10; loaded **true** | **MISSED** |
| C5. Warm submission feels immediate | mean ≤ 300 ms, max ≤ 500 ms | mean 216.0, max 262.1 | mean 231.2, max 276.5 | mean 215.0, max 260.8 | **MET** |

Raw evidence, one file per trial, in `results/`:
- `capstone_trial_1_2026-11-23_134917.md` / `.json`
- `capstone_trial_2_2026-11-23_134934.md` / `.json`
- `capstone_trial_3_2026-11-23_134947.md` / `.json`

The `.json` files hold every request body, status, response body and log line.
There's also a `_server.txt` for each trial, with the service's own console
output.

*Is it really re-running?* The model scores are identical across the three
trials (B3 is `0.2525` every time, and P1 is `0.2679`). That's expected:
GPT-2 runs on CPU in eval mode with no sampling, so the same text gets the
same perplexity. Everything else differs between trials: each one has its
own server start, `content_id`s (P1 is `bef199cb…`, `2b21dc64…`,
`ffd47e9d…`), timestamps, and timings. C5's mean moves between 215 and
231 ms, and B3's cold load between 5.9 and 6.2 s.

Output below is from **trial 1** unless marked otherwise.

**C1 output.** HTTP status and response body for each bad request, as
received by `run_capstone_trials.py::send`. The responses are produced by
`app.py::submit`, with refusals going through its inner `_reject`:

```
B1   HTTP 400  {"error": "invalid_request"}
B2   HTTP 400  {"error": "invalid_request"}
B3   HTTP 200  {"guess": "human", "combined_score": 0.2525}
B4   HTTP 400  {"error": "invalid_request"}
B5   HTTP 400  {"error": "invalid_request"}
B6   HTTP 400  {"error": "invalid_request"}
B7   HTTP 400  {"error": "invalid_request"}
B8   HTTP 400  {"error": "invalid_request"}
B9   HTTP 400  {"error": "invalid_request"}
B10  HTTP 400  {"error": "invalid_request"}
```

No 500s in any trial. The one miss is the same in all three: the keyboard
mash `"asdf qwer zxcv hjkl uiop"` is scored, and the writer is told it was
"probably written by a person".

**C2 output.** The exact line each request added to `logs/audit.jsonl`, in
order, written by `audit.py::log_rejection` (refusals) and
`audit.py::log_decision` (B3). Only `label` is cut, for width:

```jsonl
{"timestamp": "2026-11-23T11:49:19+00:00", "creator_id": "unknown", "event": "rejected", "status": "rejected", "reason": "body_not_object", "route": "/submit", "http_status": 400, "body_type": "str", "duration_ms": 1.0, "cpu_ms": 0.0}
{"timestamp": "2026-11-23T11:49:19+00:00", "creator_id": "unknown", "event": "rejected", "status": "rejected", "reason": "body_not_object", "route": "/submit", "http_status": 400, "body_type": "int", "duration_ms": 1.2, "cpu_ms": 0.0}
{"timestamp": "2026-11-23T11:49:25+00:00", "content_id": "21763d41-97bc-4971-aa8e-3d30652016c1", "creator_id": "t1-b3", "guess": "human", "model_score": 0.0049, "style_score": 0.5, "combined_score": 0.2525, "label": "We think this was probably written by a …", "status": "decided", "event": "decided", "route": "/submit", "http_status": 200, "text_chars": 24, "readable_words": 5, "text_preview": "asdf qwer zxcv hjkl uiop", "cold_start": true, "model_ms": 5913.4, "style_ms": 0.1, "duration_ms": 5914.3, "cpu_ms": 5984.4}
{"timestamp": "2026-11-23T11:49:25+00:00", "creator_id": "unknown", "event": "rejected", "status": "rejected", "reason": "body_not_object", "route": "/submit", "http_status": 400, "body_type": "list", "duration_ms": 0.6, "cpu_ms": 0.0}
{"timestamp": "2026-11-23T11:49:25+00:00", "creator_id": "t1-b5", "event": "rejected", "status": "rejected", "reason": "too_few_readable_words", "route": "/submit", "http_status": 400, "readable_words": 1, "text_chars": 2, "text_preview": "ok", "duration_ms": 0.6, "cpu_ms": 0.0}
{"timestamp": "2026-11-23T11:49:25+00:00", "creator_id": "t1-b6", "event": "rejected", "status": "rejected", "reason": "too_few_readable_words", "route": "/submit", "http_status": 400, "readable_words": 0, "text_chars": 16, "text_preview": "12345 67890 2024", "duration_ms": 0.8, "cpu_ms": 0.0}
{"timestamp": "2026-11-23T11:49:25+00:00", "creator_id": "t1-b7", "event": "rejected", "status": "rejected", "reason": "too_few_readable_words", "route": "/submit", "http_status": 400, "readable_words": 0, "text_chars": 19, "text_preview": "#### **** //// ~~~~", "duration_ms": 0.5, "cpu_ms": 0.0}
{"timestamp": "2026-11-23T11:49:25+00:00", "creator_id": "t1-b8", "event": "rejected", "status": "rejected", "reason": "too_few_readable_words", "route": "/submit", "http_status": 400, "readable_words": 0, "text_chars": 38, "text_preview": "Привет, как дела? Всё хорошо, спасибо.", "duration_ms": 0.8, "cpu_ms": 0.0}
{"timestamp": "2026-11-23T11:49:25+00:00", "creator_id": "t1-b9", "event": "rejected", "status": "rejected", "reason": "too_few_readable_words", "route": "/submit", "http_status": 400, "readable_words": 2, "text_chars": 5, "text_preview": "lol k", "duration_ms": 0.7, "cpu_ms": 0.0}
{"timestamp": "2026-11-23T11:49:25+00:00", "creator_id": "t1-b10", "event": "rejected", "status": "rejected", "reason": "too_few_readable_words", "route": "/submit", "http_status": 400, "readable_words": 1, "text_chars": 11, "text_preview": "👍👍👍 nice 👍👍", "duration_ms": 0.6, "cpu_ms": 0.0}
```

Every request left exactly one line, and every reason names the right kind
of problem: `body_not_object` for B1, B2 and B4, and `too_few_readable_words`
for the text cases. The single failure is B3, which left a `decided` record
instead of a `rejected` one. Look at `readable_words: 5`: the gate counted
the mash as five words, which is exactly the cutoff.

**C3 output.** Status, the gate's word count and the guess for each short
post, from `run_capstone_trials.py::send` and the `log_decision` lines that
`app.py::submit` wrote:

```
P1   HTTP 200  readable_words=7  guess=human  Ran 5k in 24:10 this morning, new PB!
P2   HTTP 200  readable_words=7  guess=unsure  Can't make it tonight, sorry. Next week?
P3   HTTP 200  readable_words=6  guess=human  Flight 2B delayed 3 hrs. Ugh, again.
P4   HTTP 200  readable_words=6  guess=unsure  Best ramen in town, hands down. 10/10.
P5   HTTP 200  readable_words=8  guess=unsure  Mum's birthday is on the 14th, don't forget!
P6   HTTP 200  readable_words=5  guess=human  Got 92% on the stats midterm!!
P7   HTTP 200  readable_words=6  guess=unsure  Room 4.12 is double-booked at 3pm.
P8   HTTP 200  readable_words=8  guess=human  Café on Rue Cler was closed. Went home.
P9   HTTP 200  readable_words=7  guess=human  New phone, who dis? 😂 Text me back.
P10  HTTP 200  readable_words=6  guess=unsure  Done. Finally. Sleeping now. Goodnight, everyone.
```

Met with room to spare in the count, but with no margin on one post. P6
("Got 92% on the stats midterm!!") has exactly 5 readable words, because "92%"
counts for nothing, so it's sitting right on the cutoff. P8's "Café" is
counted as "Caf", which still reaches 8.

**C4 output.** `GET /health` (`app.py::health`) at the fresh start and again
straight after the 10 bad requests:

```
{"detector_loaded": false, "detector_model": "gpt2", "log_entries": 519, "ok": true, "rate_limiting": true}
{"detector_loaded": true, "detector_model": "gpt2", "log_entries": 529, "ok": true, "rate_limiting": true}
```

Logged `duration_ms` per bad request, from the C2 lines in each trial's
`.json`:

| | B1 | B2 | B3 | B4 | B5 | B6 | B7 | B8 | B9 | B10 |
|---|---|---|---|---|---|---|---|---|---|---|
| Trial 1 | 1.0 | 1.2 | **5914.3** | 0.6 | 0.6 | 0.8 | 0.5 | 0.8 | 0.7 | 0.6 |
| Trial 2 | **18.9** | 0.8 | **6101.2** | 0.8 | 0.6 | 0.7 | 0.7 | 0.6 | 0.6 | 0.8 |
| Trial 3 | 0.6 | 0.8 | **6170.0** | 0.7 | 0.6 | 0.6 | 0.8 | 0.6 | 0.6 | 0.6 |

The model was loaded by B3 every time: its record says `cold_start: true`.
Trial 2 also has a second, separate miss. B1, the very first request after
the restart, took 18.9 ms. Here is that line from
`capstone_trial_2_2026-11-23_134934.json`:

```json
{"timestamp": "2026-11-23T11:49:35+00:00", "creator_id": "unknown", "event": "rejected", "status": "rejected", "reason": "body_not_object", "route": "/submit", "http_status": 400, "body_type": "str", "duration_ms": 18.9, "cpu_ms": 0.0}
```

**C5 output.** `measure_cost.py::main`, as captured by the harness in trial 1
(trials 2 and 3 are in their `.md` files):

```
Sending 10 submissions to http://127.0.0.1:5000/submit  (creator prefix cost-20261123-134926)
  run  1: HTTP 200
  ...
  run 10: HTTP 200

Text: 536 characters. Warm runs: 10. Cold runs: 0.

per warm run        mean       min       max
duration_ms        216.0     185.6     262.1
cpu_ms            1260.9    1000.0    1484.4
model_ms           215.0     184.5     261.2
style_ms             0.2       0.2       0.3
```

Met in all three trials. The highest single run across all 30 was 276.5 ms
(trial 2), well under the 500 ms cap. The gate and the logging cost nothing
a writer would notice: `model_ms` is within ~1 ms of `duration_ms` in every
run.
