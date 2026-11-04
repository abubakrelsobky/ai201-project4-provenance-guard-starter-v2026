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
