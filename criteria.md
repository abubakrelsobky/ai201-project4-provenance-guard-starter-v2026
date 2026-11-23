# Acceptance criteria — Provenance Guard

Five criteria that say what "working" means for this service, written in unit 7
**before** you built it.

**All five are yours.** None are given.

An acceptance criterion names a number or something plainly observable. _"The
detector is accurate"_ is an opinion — and perfect AI detection isn't possible
anyway, so it's an opinion about something nobody can deliver. _"Of 10 pieces I
wrote myself, at most 1 is labelled high-confidence AI"_ is a criterion.

Under each, write a sentence or two on **why that target**. _"I allow at most 1
false positive in 10 because on a writing site a wrong accusation costs more
than a missed detection"_ is a real answer.

> Missing your own targets next unit costs you nothing. Setting a target so
> easy you can't miss it does.

---

## Pick numbers you can defend

**Cover at least three of these five areas.** They're prompts, not a form.

| Area            | A question it could answer                                    |
| --------------- | ------------------------------------------------------------- |
| False positives | How often may a human's writing get called AI?                |
| Score spread    | How far apart should clearly-AI and clearly-human text score? |
| Label coverage  | Is every one of your three labels actually reachable?         |
| The appeal path | Does an appeal always change status and always get recorded?  |
| Bad input       | What happens when `text` is missing, empty, or enormous?      |

Two things worth knowing before you pick numbers:

- **The expensive mistake is one-sided.** Missing some AI text costs the site a
  little. Accusing a real writer costs that person a lot. A criterion that
  treats both errors as equally bad is describing a system nobody would ship.
- **Unit 8 tests across three trials, and the target has to hold across all
  three.** Your first signal runs a model, so identical input can score
  differently twice. A target of "at most 1 in 10" against trials of 2, 1, 2 is
  a **miss**.

---

## 1.

<!-- Your criterion. It must name a number. -->

When given 10 human-written samples, the AI classifier must assign the `AI` label to no more than 2 samples.

**Why this target:**
I am setting a low number because falsely accusing someone of using AI is a costly mistake. I chose 2 instead of 1 because AI detection is not conclusive proof of authorship, so the target allows a small amount of uncertainty.

---

## 2.

<!-- Your criterion. -->

For missing, empty, or whitespace-only text, the system must return an error message and must not assign an `AI`, `human`, or `unsure` label in 10 out of 10 tests.

**Why this target:**
I chose 10 out of 10 because invalid input should be handled consistently and should never be classified.

---

## 3.

In 10 test cases, the system must produce each of its three labels—`AI`, `human`, and `unsure`—at least once.

**Why this target:**
I chose this target because every label needs to be reachable for the system to be useful. Testing 10 cases gives enough opportunities to verify that none of the labels is accidentally unused.

---

## 4.

<!-- Your criterion. -->

Of 10 appeals of classifications judged correct, no more than 3 may change the classification status, and all 10 appeals must be recorded.

**Why this target:**

Because AI classification is not proof of authorship, I want to allow some valid appeals to change the result. However, if more than 3 correct classifications are overturned, the classifier may be unreliable. Recording every appeal also ensures that the appeal process works properly.

> **Revised in unit 8:** Of 10 appeals, all 10 return 200, all 10 appear in
> the audit log with status `under_review`, and in all 10 the original
> decision entry still carries the guess and label it was given.
>
> **Why revised:** the original mixes up "status" and "classification" and
> can't be measured either way. Every appeal changes the item's *status* to
> `under_review`, by design, so "no more than 3 change status" fails on every
> appeal. No appeal ever changes the *classification*, because there is no
> automatic re-check, so "no more than 3 change the classification" can't
> fail at all. Neither reading can tell a working appeal path from a broken
> one. The revision checks what the appeal path actually promises: the appeal
> is recorded, and the original decision is kept, not overwritten.

---

## 5.

<!-- Your criterion. -->

In 10 non-empty test cases, the AI classifier must assign the `unsure` label no more than 3 times.

**Why this target:**
Because the `unsure` label is useful when the evidence is unclear, but too many `unsure` results make the classifier less useful. Allowing up to 3 out of 10 cases gives the system some uncertainty without allowing it to avoid making a classification too often.

---

<!-- ─────────────────────────────────────────────────────────────────────────
     UNIT 8 — read this before you change anything above.

     If a criterion turns out to be BROKEN rather than merely unmet, you can
     revise it, and that earns credit. But never delete or edit the original
     line. Add the revision underneath, like this:

         ## 2. Uncertain cases land in the unsure band

         The system handles uncertain cases well.

         **Why this target:** ...

         > **Revised in unit 8:** Text I judged borderline scores between
         > 0.4 and 0.6 in at least 4 of 5 cases.
         >
         > **Why revised:** "well" gave me nothing to check. I couldn't
         > reach a verdict from it at all.

     That's a revision because the criterion couldn't be MEASURED.

     Lowering a target because you missed it is not a revision, and it costs
     you the point:

         ✗ "At most 1 of 10 of my own pieces flagged as AI" → "at most 3
            of 10", because 1 of 10 turned out to be hard.

     A number you missed stays where it is, gets diagnosed, and gets a fix
     attempted. That's where the points are.
     ───────────────────────────────────────────────────────────────────────── -->

---

# Capstone criteria

Written in the capstone unit, **after** the input gate was built (Milestone 2)
and instrumented (Milestone 3), and **before** any trial was run. Nothing above
this line was changed. C1–C4 are about the extension (the input gate on
`/submit`). C5 is about the system as it already worked.

Every criterion runs **three trials**, and the target has to hold in all three.
A miss in any trial is a miss.

The test inputs are fixed here, before any run, so they can't drift toward
whatever passes. None of them come from unit 8's attack set.

**Bad-request set (used by C1, C2, C4).** Ten requests, each with a fresh
`creator_id` where there is one:

| # | What's wrong | Body sent |
|---|---|---|
| B1 | body is a JSON string | `"please check my essay"` |
| B2 | body is a JSON number | `42` |
| B3 | body is a JSON boolean | `true` |
| B4 | body is an array holding a valid submission | `[{"text": "A perfectly normal sentence about my weekend plans.", "creator_id": "b4"}]` |
| B5 | text is one short word | `{"text": "ok", "creator_id": "b5"}` |
| B6 | text is only digits | `{"text": "12345 67890 2024", "creator_id": "b6"}` |
| B7 | text is only symbols | `{"text": "#### **** //// ~~~~", "creator_id": "b7"}` |
| B8 | text is Cyrillic | `{"text": "Привет, как дела? Всё хорошо, спасибо.", "creator_id": "b8"}` |
| B9 | text is two words | `{"text": "lol k", "creator_id": "b9"}` |
| B10 | text is emoji around one word | `{"text": "👍👍👍 nice 👍👍", "creator_id": "b10"}` |

B8 and B10 are sent from a UTF-8 file, never typed into Git Bash (Milestone 3
showed that turns them into `?`).

**Short-real-post set (used by C3).** Ten genuine short posts of the kind a
person writes. Each one has at least 5 words as a person would count them
(so "5k", "24:10" and "Café" each count as one):

1. Ran 5k in 24:10 this morning, new PB!
2. Can't make it tonight, sorry. Next week?
3. Flight 2B delayed 3 hrs. Ugh, again.
4. Best ramen in town, hands down. 10/10.
5. Mum's birthday is on the 14th, don't forget!
6. Got 92% on the stats midterm!!
7. Room 4.12 is double-booked at 3pm.
8. Café on Rue Cler was closed. Went home.
9. New phone, who dis? 😂 Text me back.
10. Done. Finally. Sleeping now. Goodnight, everyone.

---

## C1. Bad requests are refused, never crashed on and never labelled

Of the 10 requests in the bad-request set, **10 of 10 get HTTP 400, 0 get a
500, and 0 come back with a `guess` or `label`**, in each of 3 trials.

**Why this target:** the extension's whole claim is that a bad request gets a
clear refusal instead of a crash or a made-up label. There's no "mostly" in
that. One 500 means the gate has a hole, and one label on non-text means the
service invented a judgement about writing that isn't there. Both happened
before the gate (MF02, RQ07, MF03–MF07), so 10/10 is the only number that says
the gate fixed the class of problem and not just the ten inputs it was built
against.

---

## C2. Every refusal leaves exactly one record that says why

For each of the 10 bad requests, `logs/audit.jsonl` gains **exactly one**
entry with `status: "rejected"`, `http_status: 400`, a non-empty `reason`, and
a numeric `duration_ms`. **10 of 10 in each of 3 trials**, and no request
leaves zero or two entries.

**Why this target:** a refusal nobody can find later is the same as a failure
that shows up only as an absence. Before the gate, RQ07 and MF02 left *no*
record at all. "Exactly one" matters in both directions. Zero means it's
invisible, and two means the log over-counts traffic and any rate or cost
worked out from it is wrong. Without `reason` you can't tell a malformed
body from a too-short text, and that's the first question you'd ask.

---

## C3. Real short posts are not turned away by the gate

Of the 10 posts in the short-real-post set, **at most 1 is refused** (gets a
400 instead of a label), in each of 3 trials.

**Why this target:** this is what the gate costs. A refusal on real writing
is a writer turned away with "we couldn't find enough words" when the words
are right there. That's less harmful than a false accusation, but it's the
same kind of mistake: the system being wrong about a real person. I allow 1
because 5 words is a blunt line and very short posts are where it bites. More
than 1 in 10 would mean the gate is throwing out ordinary writing, not junk.
This criterion only checks *whether* the post is scored, not which label it
gets. Label quality on short texts is the signals' problem, and that's out of
scope.

---

## C4. A refused request never touches the model

On a **freshly started** service (`python app.py`, nothing sent yet), send the
10 bad requests first. Then **all 10 have `duration_ms` under 5 ms**, and
`GET /health` still reports **`"detector_loaded": false`**. In each of 3
trials, with a restart before each one.

**Why this target:** the gate is supposed to stand *in front of* the
signals, not beside them. If a junk request loaded GPT-2, it would cost a
~6 s cold start and ~1 GB of memory (Milestone 3's numbers) to say "no". An
attacker could also keep a service busy with requests that are refused
anyway. `detector_loaded: false` after ten refusals proves the model was never
reached. 5 ms is roughly ten times what a refusal took in the Milestone 3
session (0.5–0.8 ms), so missing it would mean real work is happening before
the refusal, not timer noise.

---

## C5. A warm submission answers fast enough to feel immediate

With the service already **warm** (one throwaway submission sent first and
excluded), `python measure_cost.py` (10 submissions of the same ~100-word
paragraph) shows **mean `duration_ms` ≤ 300 ms and no single run over
500 ms**, in each of 3 trials. The cold-start request is excluded on
purpose and reported separately, not counted toward this target.

**Why this target:** a writer pastes a paragraph and waits for a verdict.
Around a third of a second still feels like an immediate answer, and
anything slower starts to feel like the page is thinking. The 500 ms cap on
any single run is there because an average can hide one slow outlier, and a
writer experiences the outlier, not the mean. It says *warm* because a
locally started service loads GPT-2 on its first scored request (5.8 s in
Milestone 3). Counting that would measure the start-up, not the service.
This one isn't about the extension. It checks that adding the gate and the
instrumentation didn't make the good path slower in a way a writer would
notice.
