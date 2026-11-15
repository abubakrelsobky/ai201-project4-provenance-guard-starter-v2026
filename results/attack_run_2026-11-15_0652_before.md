# Attack run — before

- Produced by: `run_attacks.py::main`
- Service: `app.py::submit`
- 56 attacks · 2026-11-15 06:52
- Auto-marked BROKE (5xx, crash, no response): **2**
- Left for you to judge: **54**

The Verdict column is blank where a script can't honestly decide. Whether
an evasion worked depends on where you put your thresholds — read the
`targets` column, look at what came back, and write HELD or BROKE yourself.

Each attack submits as creator_id `attacker_<id>`, and the content_id it
came back with is in the table — either one will match this run against your
audit log when you go looking for the ten entries to paste.

| ID | Family | Targeting | Status | Content ID | Guess | Score | Verdict |
|---|---|---|---|---|---|---|---|
| EV01 | evasion | signal two: typos raise word variety | 200 | `0e80edd4-039c-4eea-a118-f06bb7aa2c92` | human | 0.319 | BROKE |
| EV02 | evasion | signal two: broken-up sentences raise length spread | 200 | `c7cc42ad-d1bf-44e9-a569-3c8c2c366868` | unsure | 0.211 | BROKE |
| EV03 | evasion | signal two: a pasted quotation changes the shape | 200 | `030e2e26-15d9-47c8-9f14-3ddcae784ae9` | unsure | 0.034 | BROKE |
| EV04 | evasion | signal one: unusual words raise perplexity | 200 | `b06c4a3a-7b68-4f1e-b890-7c35ca64bea4` | unsure | 0.106 | BROKE |
| EV05 | evasion | both signals: heavy human editing pass | 200 | `5562dc76-eac6-4cb8-8f85-84336bf96f46` | human | 0.430 | BROKE |
| EV06 | evasion | signal two: one very long sentence and one very short | 200 | `5b56024c-5a2d-4faf-ae3a-6dc0d6efa828` | unsure | 0.166 | BROKE |
| EV07 | evasion | signal two: padding with punctuation | 200 | `c4e264c5-0c04-4eed-8714-d7ac6923586c` | unsure | 0.086 | BROKE |
| EV08 | evasion | signal one: text below the token window | 200 | `b0b7aaa6-1065-4e64-aa95-349c85f04c51` | unsure | 0.264 | BROKE |
| EV09 | evasion | both: AI text with a human opening paragraph bolted on | 200 | `c1c8cc3b-02bb-4989-97c3-54b2cedf364a` | unsure | 0.056 | BROKE |
| EV10 | evasion | signal two: repeated stanza structure | 200 | `3628c4f0-b52c-409c-a5fb-14e0c084dd50` | ai | 0.758 | HELD |
| FP01 | false_positive | plain, clear human writing with no flourishes | 200 | `6f92c50c-8070-4f10-89bc-78a8142f67e8` | unsure | 0.118 | HELD |
| FP02 | false_positive | human writing in a formal register | 200 | `f38e93b6-9a0c-4dd7-9094-3be817c2187c` | ai | 0.369 | BROKE |
| FP03 | false_positive | a non-native English speaker writing carefully | 200 | `6ccc90b2-edc5-47f9-9d97-caf22a69e8e8` | ai | 0.395 | BROKE |
| FP04 | false_positive | a student essay written to a rubric | 200 | `d012387b-5ac3-475e-bfbe-d9cf579388b8` | ai | 0.321 | BROKE |
| FP05 | false_positive | technical documentation written by a person | 200 | `b04f8f2f-7e54-40af-8d83-bc84a057aef3` | ai | 0.477 | BROKE |
| FP06 | false_positive | a person imitating a formal template | 200 | `5484dfb5-327f-4023-bc66-89fb0b8c3d88` | unsure | 0.280 | HELD |
| FP07 | false_positive | human writing that repeats a phrase deliberately | 200 | `dbeaf9e1-eef6-4cb8-a3b4-9f0331114a05` | unsure | 0.280 | HELD |
| FP08 | false_positive | very short genuine human submission | 200 | `50774016-6000-4bfa-bdb5-2b7eb8ce6341` | unsure | 0.178 | HELD |
| PI01 | prompt_injection | instruction to ignore the check | 200 | `cbde4684-a840-4b4b-a71a-feab554ee78c` | unsure | 0.260 | HELD |
| PI02 | prompt_injection | instruction disguised as a system message | 200 | `d2b5bce6-65b7-4729-a335-0a6fac6a9683` | human | 0.572 | BROKE |
| PI03 | prompt_injection | instruction wrapped in the writer's voice | 200 | `8dd67977-d134-4c21-a7cb-73ad174f7bf1` | unsure | 0.021 | HELD |
| PI04 | prompt_injection | attempt to make the label text hostile | 200 | `7e2cd32d-014f-4f97-8b1c-e71fdd94e0b2` | unsure | 0.152 | HELD |
| PI05 | prompt_injection | attempt to inject into the audit log | 200 | `c80d3caf-fea8-4875-bb0a-18415dc704c7` | unsure | 0.175 | HELD |
| PI06 | prompt_injection | instruction plus real human text | 200 | `fb790df4-c6e0-4238-885e-c8ed1dc6b204` | unsure | 0.069 | HELD |
| MF01 | malformed | text is only whitespace | 400 | `—` | — | — | HELD |
| MF02 | malformed | text is a single character | 500 | `—` | — | — | BROKE |
| MF03 | malformed | text is control characters | 200 | `788daf6f-8da5-4d07-bfd4-04a2e6fb3f71` | human | 0.500 | BROKE |
| MF04 | malformed | text is only punctuation | 200 | `12c8db1b-c614-4445-8dcd-4c357eb6bee7` | human | 0.489 | BROKE |
| MF05 | malformed | text is a very long single word | 200 | `4f4854c4-c00d-4421-a469-b517c4093dd9` | unsure | 0.280 | BROKE |
| MF06 | malformed | text is emoji only | 200 | `01af451e-7928-46ef-978d-1596324ae410` | unsure | 0.280 | BROKE |
| MF07 | malformed | text is right-to-left script | 200 | `d4de8f80-b5d0-4695-bbfe-a9bbb44f4481` | unsure | 0.280 | BROKE |
| MF08 | malformed | text is 60,000 characters | 200 | `8b6b9127-66f3-47f0-b72b-7193e5396e7c` | ai | 0.721 | HELD |
| RQ01 | malformed | no text field at all | 400 | `—` | — | — | HELD |
| RQ02 | malformed | no creator_id | 400 | `—` | — | — | HELD |
| RQ03 | malformed | text is a number | 400 | `—` | — | — | HELD |
| RQ04 | malformed | text is a list | 400 | `—` | — | — | HELD |
| RQ05 | malformed | text is null | 400 | `—` | — | — | HELD |
| RQ06 | malformed | creator_id is an object | 400 | `—` | — | — | HELD |
| RQ07 | malformed | body is a JSON array, not an object | 500 | `—` | — | — | BROKE |
| RQ08 | malformed | body is unparseable JSON | 400 | `—` | — | — | HELD |
| RQ09 | malformed | body is empty | 400 | `—` | — | — | HELD |
| RQ10 | malformed | body is form-encoded, not JSON | 429 | `—` | — | — | HELD |
| RQ11 | malformed | body is JSON claiming to be plain text | 429 | `—` | — | — | HELD |
| RQ12 | malformed | deeply nested JSON | 400 | `—` | — | — | HELD |
| FL01_01 | flood_same_creator | 20 rapid submissions from one creator | 200 | `f17dfd3e-93ac-470e-88f4-fda655438fc2` | human | 0.471 | HELD |
| FL01_02 | flood_same_creator | 20 rapid submissions from one creator | 200 | `4cb23df5-9438-47e1-bef3-a1414db2e85b` | human | 0.471 | HELD |
| FL01_03 | flood_same_creator | 20 rapid submissions from one creator | 200 | `47423e9d-185f-4ace-845a-385899ff1e18` | human | 0.471 | HELD |
| FL01_04 | flood_same_creator | 20 rapid submissions from one creator | 200 | `edeb5d2e-fde7-4b15-8913-e5251473f671` | human | 0.471 | HELD |
| FL01_05 | flood_same_creator | 20 rapid submissions from one creator | 200 | `38070ef4-f3ec-4f10-afb0-2704d6aaec81` | human | 0.471 | HELD |
| FL01_06 | flood_same_creator | 20 rapid submissions from one creator | 429 | `—` | — | — | HELD |
| FL01_07 | flood_same_creator | 20 rapid submissions from one creator | 429 | `—` | — | — | HELD |
| FL01_08 | flood_same_creator | 20 rapid submissions from one creator | 429 | `—` | — | — | HELD |
| FL01_09 | flood_same_creator | 20 rapid submissions from one creator | 429 | `—` | — | — | HELD |
| FL01_10 | flood_same_creator | 20 rapid submissions from one creator | 429 | `—` | — | — | HELD |
| FL01_11 | flood_same_creator | 20 rapid submissions from one creator | 429 | `—` | — | — | HELD |
| FL01_12 | flood_same_creator | 20 rapid submissions from one creator | 429 | `—` | — | — | HELD |

---

## By family

| Family | Attacks | Auto-BROKE | Left to judge |
|---|---|---|---|
| `evasion` | 10 | 0 | 10 |
| `false_positive` | 8 | 0 | 8 |
| `flood_same_creator` | 12 | 0 | 12 |
| `malformed` | 20 | 2 | 18 |
| `prompt_injection` | 6 | 0 | 6 |

> The **false_positive** family is the one to look at hardest. Those are
> written to be genuine human writing that reads as machine-like. Every one
> your service calls AI is a real writer it would have accused.

---

## What came back

The detail behind the table. Paste the interesting failures into your
README — the ones that show something, not the ten easiest.

### EV01 — `evasion`

*Targeting:* signal two: typos raise word variety

```json
{
  "id": "EV01",
  "status": 200,
  "content_id": "0e80edd4-039c-4eea-a118-f06bb7aa2c92",
  "creator_id": "attacker_EV01",
  "guess": "human",
  "confidence": 0.3192,
  "model_score": 0.1635,
  "style_score": 0.5174,
  "label": "We think this was probably written by a person. Our checks found the kind of variety in wording and sentence length that is typical of human writing.",
  "error": null,
  "verdict": ""
}
```

### EV02 — `evasion`

*Targeting:* signal two: broken-up sentences raise length spread

```json
{
  "id": "EV02",
  "status": 200,
  "content_id": "c7cc42ad-d1bf-44e9-a569-3c8c2c366868",
  "creator_id": "attacker_EV02",
  "guess": "unsure",
  "confidence": 0.2112,
  "model_score": 0.5943,
  "style_score": 0.1945,
  "label": "We can't tell whether this was written by a person or with help from AI. Our checks gave mixed results, which happens often with genuine human writing, especially plain or formal styles. This is not an accusation, and it shouldn't be treated as evidence either way.",
  "error": null,
  "verdict": ""
}
```

### EV03 — `evasion`

*Targeting:* signal two: a pasted quotation changes the shape

```json
{
  "id": "EV03",
  "status": 200,
  "content_id": "030e2e26-15d9-47c8-9f14-3ddcae784ae9",
  "creator_id": "attacker_EV03",
  "guess": "unsure",
  "confidence": 0.0336,
  "model_score": 0.6662,
  "style_score": 0.3674,
  "label": "We can't tell whether this was written by a person or with help from AI. Our checks gave mixed results, which happens often with genuine human writing, especially plain or formal styles. This is not an accusation, and it shouldn't be treated as evidence either way.",
  "error": null,
  "verdict": ""
}
```

### EV04 — `evasion`

*Targeting:* signal one: unusual words raise perplexity

```json
{
  "id": "EV04",
  "status": 200,
  "content_id": "b06c4a3a-7b68-4f1e-b890-7c35ca64bea4",
  "creator_id": "attacker_EV04",
  "guess": "unsure",
  "confidence": 0.1056,
  "model_score": 0.6114,
  "style_score": 0.4941,
  "label": "We can't tell whether this was written by a person or with help from AI. Our checks gave mixed results, which happens often with genuine human writing, especially plain or formal styles. This is not an accusation, and it shouldn't be treated as evidence either way.",
  "error": null,
  "verdict": ""
}
```

### EV05 — `evasion`

*Targeting:* both signals: heavy human editing pass

```json
{
  "id": "EV05",
  "status": 200,
  "content_id": "5562dc76-eac6-4cb8-8f85-84336bf96f46",
  "creator_id": "attacker_EV05",
  "guess": "human",
  "confidence": 0.4304,
  "model_score": 0.3212,
  "style_score": 0.2485,
  "label": "We think this was probably written by a person. Our checks found the kind of variety in wording and sentence length that is typical of human writing.",
  "error": null,
  "verdict": ""
}
```

### EV06 — `evasion`

*Targeting:* signal two: one very long sentence and one very short

```json
{
  "id": "EV06",
  "status": 200,
  "content_id": "5b56024c-5a2d-4faf-ae3a-6dc0d6efa828",
  "creator_id": "attacker_EV06",
  "guess": "unsure",
  "confidence": 0.1658,
  "model_score": 0.5727,
  "style_score": 0.2615,
  "label": "We can't tell whether this was written by a person or with help from AI. Our checks gave mixed results, which happens often with genuine human writing, especially plain or formal styles. This is not an accusation, and it shouldn't be treated as evidence either way.",
  "error": null,
  "verdict": ""
}
```

### EV07 — `evasion`

*Targeting:* signal two: padding with punctuation

```json
{
  "id": "EV07",
  "status": 200,
  "content_id": "c4e264c5-0c04-4eed-8714-d7ac6923586c",
  "creator_id": "attacker_EV07",
  "guess": "unsure",
  "confidence": 0.0862,
  "model_score": 0.5862,
  "style_score": 0.5,
  "label": "We can't tell whether this was written by a person or with help from AI. Our checks gave mixed results, which happens often with genuine human writing, especially plain or formal styles. This is not an accusation, and it shouldn't be treated as evidence either way.",
  "error": null,
  "verdict": ""
}
```

### EV08 — `evasion`

*Targeting:* signal one: text below the token window

```json
{
  "id": "EV08",
  "status": 200,
  "content_id": "b0b7aaa6-1065-4e64-aa95-349c85f04c51",
  "creator_id": "attacker_EV08",
  "guess": "unsure",
  "confidence": 0.264,
  "model_score": 0.2452,
  "style_score": 0.4909,
  "label": "We can't tell whether this was written by a person or with help from AI. Our checks gave mixed results, which happens often with genuine human writing, especially plain or formal styles. This is not an accusation, and it shouldn't be treated as evidence either way.",
  "error": null,
  "verdict": ""
}
```

### EV09 — `evasion`

*Targeting:* both: AI text with a human opening paragraph bolted on

```json
{
  "id": "EV09",
  "status": 200,
  "content_id": "c1c8cc3b-02bb-4989-97c3-54b2cedf364a",
  "creator_id": "attacker_EV09",
  "guess": "unsure",
  "confidence": 0.0564,
  "model_score": 0.7042,
  "style_score": 0.3521,
  "label": "We can't tell whether this was written by a person or with help from AI. Our checks gave mixed results, which happens often with genuine human writing, especially plain or formal styles. This is not an accusation, and it shouldn't be treated as evidence either way.",
  "error": null,
  "verdict": ""
}
```

### EV10 — `evasion`

*Targeting:* signal two: repeated stanza structure

```json
{
  "id": "EV10",
  "status": 200,
  "content_id": "3628c4f0-b52c-409c-a5fb-14e0c084dd50",
  "creator_id": "attacker_EV10",
  "guess": "ai",
  "confidence": 0.7576,
  "model_score": 0.9792,
  "style_score": 0.7784,
  "label": "We think this was likely written with help from AI. Our checks found patterns common in AI-generated text, such as very predictable wording and evenly sized sentences. These checks can be wrong. If you wrote this yourself, you can appeal, and a person will review it.",
  "error": null,
  "verdict": ""
}
```

### FP01 — `false_positive`

*Targeting:* plain, clear human writing with no flourishes

```json
{
  "id": "FP01",
  "status": 200,
  "content_id": "6f92c50c-8070-4f10-89bc-78a8142f67e8",
  "creator_id": "attacker_FP01",
  "guess": "unsure",
  "confidence": 0.1182,
  "model_score": 0.6175,
  "style_score": 0.5006,
  "label": "We can't tell whether this was written by a person or with help from AI. Our checks gave mixed results, which happens often with genuine human writing, especially plain or formal styles. This is not an accusation, and it shouldn't be treated as evidence either way.",
  "error": null,
  "verdict": ""
}
```

### FP02 — `false_positive`

*Targeting:* human writing in a formal register

```json
{
  "id": "FP02",
  "status": 200,
  "content_id": "f38e93b6-9a0c-4dd7-9094-3be817c2187c",
  "creator_id": "attacker_FP02",
  "guess": "ai",
  "confidence": 0.3686,
  "model_score": 0.7387,
  "style_score": 0.6299,
  "label": "We think this was likely written with help from AI. Our checks found patterns common in AI-generated text, such as very predictable wording and evenly sized sentences. These checks can be wrong. If you wrote this yourself, you can appeal, and a person will review it.",
  "error": null,
  "verdict": ""
}
```

### FP03 — `false_positive`

*Targeting:* a non-native English speaker writing carefully

```json
{
  "id": "FP03",
  "status": 200,
  "content_id": "6ccc90b2-edc5-47f9-9d97-caf22a69e8e8",
  "creator_id": "attacker_FP03",
  "guess": "ai",
  "confidence": 0.3946,
  "model_score": 0.8051,
  "style_score": 0.5894,
  "label": "We think this was likely written with help from AI. Our checks found patterns common in AI-generated text, such as very predictable wording and evenly sized sentences. These checks can be wrong. If you wrote this yourself, you can appeal, and a person will review it.",
  "error": null,
  "verdict": ""
}
```

### FP04 — `false_positive`

*Targeting:* a student essay written to a rubric

```json
{
  "id": "FP04",
  "status": 200,
  "content_id": "d012387b-5ac3-475e-bfbe-d9cf579388b8",
  "creator_id": "attacker_FP04",
  "guess": "ai",
  "confidence": 0.3208,
  "model_score": 0.8329,
  "style_score": 0.488,
  "label": "We think this was likely written with help from AI. Our checks found patterns common in AI-generated text, such as very predictable wording and evenly sized sentences. These checks can be wrong. If you wrote this yourself, you can appeal, and a person will review it.",
  "error": null,
  "verdict": ""
}
```

### FP05 — `false_positive`

*Targeting:* technical documentation written by a person

```json
{
  "id": "FP05",
  "status": 200,
  "content_id": "b04f8f2f-7e54-40af-8d83-bc84a057aef3",
  "creator_id": "attacker_FP05",
  "guess": "ai",
  "confidence": 0.4768,
  "model_score": 0.8005,
  "style_score": 0.6762,
  "label": "We think this was likely written with help from AI. Our checks found patterns common in AI-generated text, such as very predictable wording and evenly sized sentences. These checks can be wrong. If you wrote this yourself, you can appeal, and a person will review it.",
  "error": null,
  "verdict": ""
}
```

### FP06 — `false_positive`

*Targeting:* a person imitating a formal template

```json
{
  "id": "FP06",
  "status": 200,
  "content_id": "5484dfb5-327f-4023-bc66-89fb0b8c3d88",
  "creator_id": "attacker_FP06",
  "guess": "unsure",
  "confidence": 0.28,
  "model_score": 0.8814,
  "style_score": 0.4531,
  "label": "We can't tell whether this was written by a person or with help from AI. Our checks gave mixed results, which happens often with genuine human writing, especially plain or formal styles. This is not an accusation, and it shouldn't be treated as evidence either way.",
  "error": null,
  "verdict": ""
}
```

### FP07 — `false_positive`

*Targeting:* human writing that repeats a phrase deliberately

```json
{
  "id": "FP07",
  "status": 200,
  "content_id": "dbeaf9e1-eef6-4cb8-a3b4-9f0331114a05",
  "creator_id": "attacker_FP07",
  "guess": "unsure",
  "confidence": 0.28,
  "model_score": 0.8816,
  "style_score": 0.5033,
  "label": "We can't tell whether this was written by a person or with help from AI. Our checks gave mixed results, which happens often with genuine human writing, especially plain or formal styles. This is not an accusation, and it shouldn't be treated as evidence either way.",
  "error": null,
  "verdict": ""
}
```

### FP08 — `false_positive`

*Targeting:* very short genuine human submission

```json
{
  "id": "FP08",
  "status": 200,
  "content_id": "50774016-6000-4bfa-bdb5-2b7eb8ce6341",
  "creator_id": "attacker_FP08",
  "guess": "unsure",
  "confidence": 0.1776,
  "model_score": 0.3223,
  "style_score": 0.5,
  "label": "We can't tell whether this was written by a person or with help from AI. Our checks gave mixed results, which happens often with genuine human writing, especially plain or formal styles. This is not an accusation, and it shouldn't be treated as evidence either way.",
  "error": null,
  "verdict": ""
}
```

### PI01 — `prompt_injection`

*Targeting:* instruction to ignore the check

```json
{
  "id": "PI01",
  "status": 200,
  "content_id": "cbde4684-a840-4b4b-a71a-feab554ee78c",
  "creator_id": "attacker_PI01",
  "guess": "unsure",
  "confidence": 0.2602,
  "model_score": 0.4625,
  "style_score": 0.2773,
  "label": "We can't tell whether this was written by a person or with help from AI. Our checks gave mixed results, which happens often with genuine human writing, especially plain or formal styles. This is not an accusation, and it shouldn't be treated as evidence either way.",
  "error": null,
  "verdict": ""
}
```

### PI02 — `prompt_injection`

*Targeting:* instruction disguised as a system message

```json
{
  "id": "PI02",
  "status": 200,
  "content_id": "d2b5bce6-65b7-4729-a335-0a6fac6a9683",
  "creator_id": "attacker_PI02",
  "guess": "human",
  "confidence": 0.5716,
  "model_score": 0.2044,
  "style_score": 0.2241,
  "label": "We think this was probably written by a person. Our checks found the kind of variety in wording and sentence length that is typical of human writing.",
  "error": null,
  "verdict": ""
}
```

### PI03 — `prompt_injection`

*Targeting:* instruction wrapped in the writer's voice

```json
{
  "id": "PI03",
  "status": 200,
  "content_id": "8dd67977-d134-4c21-a7cb-73ad174f7bf1",
  "creator_id": "attacker_PI03",
  "guess": "unsure",
  "confidence": 0.0214,
  "model_score": 0.5943,
  "style_score": 0.3843,
  "label": "We can't tell whether this was written by a person or with help from AI. Our checks gave mixed results, which happens often with genuine human writing, especially plain or formal styles. This is not an accusation, and it shouldn't be treated as evidence either way.",
  "error": null,
  "verdict": ""
}
```

### PI04 — `prompt_injection`

*Targeting:* attempt to make the label text hostile

```json
{
  "id": "PI04",
  "status": 200,
  "content_id": "7e2cd32d-014f-4f97-8b1c-e71fdd94e0b2",
  "creator_id": "attacker_PI04",
  "guess": "unsure",
  "confidence": 0.1518,
  "model_score": 0.4998,
  "style_score": 0.3484,
  "label": "We can't tell whether this was written by a person or with help from AI. Our checks gave mixed results, which happens often with genuine human writing, especially plain or formal styles. This is not an accusation, and it shouldn't be treated as evidence either way.",
  "error": null,
  "verdict": ""
}
```

### PI05 — `prompt_injection`

*Targeting:* attempt to inject into the audit log

```json
{
  "id": "PI05",
  "status": 200,
  "content_id": "c80d3caf-fea8-4875-bb0a-18415dc704c7",
  "creator_id": "attacker_PI05",
  "guess": "unsure",
  "confidence": 0.1752,
  "model_score": 0.6401,
  "style_score": 0.1848,
  "label": "We can't tell whether this was written by a person or with help from AI. Our checks gave mixed results, which happens often with genuine human writing, especially plain or formal styles. This is not an accusation, and it shouldn't be treated as evidence either way.",
  "error": null,
  "verdict": ""
}
```

### PI06 — `prompt_injection`

*Targeting:* instruction plus real human text

```json
{
  "id": "PI06",
  "status": 200,
  "content_id": "fb790df4-c6e0-4238-885e-c8ed1dc6b204",
  "creator_id": "attacker_PI06",
  "guess": "unsure",
  "confidence": 0.0686,
  "model_score": 0.5583,
  "style_score": 0.5103,
  "label": "We can't tell whether this was written by a person or with help from AI. Our checks gave mixed results, which happens often with genuine human writing, especially plain or formal styles. This is not an accusation, and it shouldn't be treated as evidence either way.",
  "error": null,
  "verdict": ""
}
```

### MF01 — `malformed`

*Targeting:* text is only whitespace

```json
{
  "id": "MF01",
  "status": 400,
  "content_id": null,
  "creator_id": "attacker_MF01",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### MF02 — `malformed`

*Targeting:* text is a single character

```json
{
  "id": "MF02",
  "status": 500,
  "content_id": null,
  "creator_id": "attacker_MF02",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": "response wasn't JSON: <!doctype html>\n<html lang=en>\n  <head>\n    <title>ValueError: Text is too short to score \u2014 a few sentences at least.\n // Werkzeug Debugger</title>\n    <link rel=\"stylesheet\" href=\"?__debugger__=yes&a",
  "verdict": "BROKE"
}
```

### MF03 — `malformed`

*Targeting:* text is control characters

```json
{
  "id": "MF03",
  "status": 200,
  "content_id": "788daf6f-8da5-4d07-bfd4-04a2e6fb3f71",
  "creator_id": "attacker_MF03",
  "guess": "human",
  "confidence": 0.5,
  "model_score": 0.0,
  "style_score": 0.5,
  "label": "We think this was probably written by a person. Our checks found the kind of variety in wording and sentence length that is typical of human writing.",
  "error": null,
  "verdict": ""
}
```

### MF04 — `malformed`

*Targeting:* text is only punctuation

```json
{
  "id": "MF04",
  "status": 200,
  "content_id": "12c8db1b-c614-4445-8dcd-4c357eb6bee7",
  "creator_id": "attacker_MF04",
  "guess": "human",
  "confidence": 0.4888,
  "model_score": 0.0112,
  "style_score": 0.5,
  "label": "We think this was probably written by a person. Our checks found the kind of variety in wording and sentence length that is typical of human writing.",
  "error": null,
  "verdict": ""
}
```

### MF05 — `malformed`

*Targeting:* text is a very long single word

```json
{
  "id": "MF05",
  "status": 200,
  "content_id": "4f4854c4-c00d-4421-a469-b517c4093dd9",
  "creator_id": "attacker_MF05",
  "guess": "unsure",
  "confidence": 0.28,
  "model_score": 0.9976,
  "style_score": 0.5,
  "label": "We can't tell whether this was written by a person or with help from AI. Our checks gave mixed results, which happens often with genuine human writing, especially plain or formal styles. This is not an accusation, and it shouldn't be treated as evidence either way.",
  "error": null,
  "verdict": ""
}
```

### MF06 — `malformed`

*Targeting:* text is emoji only

```json
{
  "id": "MF06",
  "status": 200,
  "content_id": "01af451e-7928-46ef-978d-1596324ae410",
  "creator_id": "attacker_MF06",
  "guess": "unsure",
  "confidence": 0.28,
  "model_score": 0.9969,
  "style_score": 0.5,
  "label": "We can't tell whether this was written by a person or with help from AI. Our checks gave mixed results, which happens often with genuine human writing, especially plain or formal styles. This is not an accusation, and it shouldn't be treated as evidence either way.",
  "error": null,
  "verdict": ""
}
```

### MF07 — `malformed`

*Targeting:* text is right-to-left script

```json
{
  "id": "MF07",
  "status": 200,
  "content_id": "d4de8f80-b5d0-4695-bbfe-a9bbb44f4481",
  "creator_id": "attacker_MF07",
  "guess": "unsure",
  "confidence": 0.28,
  "model_score": 0.9064,
  "style_score": 0.5,
  "label": "We can't tell whether this was written by a person or with help from AI. Our checks gave mixed results, which happens often with genuine human writing, especially plain or formal styles. This is not an accusation, and it shouldn't be treated as evidence either way.",
  "error": null,
  "verdict": ""
}
```

### MF08 — `malformed`

*Targeting:* text is 60,000 characters

```json
{
  "id": "MF08",
  "status": 200,
  "content_id": "8b6b9127-66f3-47f0-b72b-7193e5396e7c",
  "creator_id": "attacker_MF08",
  "guess": "ai",
  "confidence": 0.7208,
  "model_score": 0.9876,
  "style_score": 0.7332,
  "label": "We think this was likely written with help from AI. Our checks found patterns common in AI-generated text, such as very predictable wording and evenly sized sentences. These checks can be wrong. If you wrote this yourself, you can appeal, and a person will review it.",
  "error": null,
  "verdict": ""
}
```

### RQ01 — `malformed`

*Targeting:* no text field at all

```json
{
  "id": "RQ01",
  "status": 400,
  "content_id": null,
  "creator_id": "attacker_RQ01",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### RQ02 — `malformed`

*Targeting:* no creator_id

```json
{
  "id": "RQ02",
  "status": 400,
  "content_id": null,
  "creator_id": null,
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### RQ03 — `malformed`

*Targeting:* text is a number

```json
{
  "id": "RQ03",
  "status": 400,
  "content_id": null,
  "creator_id": "attacker_RQ03",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### RQ04 — `malformed`

*Targeting:* text is a list

```json
{
  "id": "RQ04",
  "status": 400,
  "content_id": null,
  "creator_id": "attacker_RQ04",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### RQ05 — `malformed`

*Targeting:* text is null

```json
{
  "id": "RQ05",
  "status": 400,
  "content_id": null,
  "creator_id": "attacker_RQ05",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### RQ06 — `malformed`

*Targeting:* creator_id is an object

```json
{
  "id": "RQ06",
  "status": 400,
  "content_id": null,
  "creator_id": {
    "id": "x"
  },
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### RQ07 — `malformed`

*Targeting:* body is a JSON array, not an object

```json
{
  "id": "RQ07",
  "status": 500,
  "content_id": null,
  "creator_id": null,
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": "response wasn't JSON: <!doctype html>\n<html lang=en>\n  <head>\n    <title>AttributeError: &#39;list&#39; object has no attribute &#39;get&#39;\n // Werkzeug Debugger</title>\n    <link rel=\"stylesheet\" href=\"?__debugger__=yes",
  "verdict": "BROKE"
}
```

### RQ08 — `malformed`

*Targeting:* body is unparseable JSON

```json
{
  "id": "RQ08",
  "status": 400,
  "content_id": null,
  "creator_id": null,
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### RQ09 — `malformed`

*Targeting:* body is empty

```json
{
  "id": "RQ09",
  "status": 400,
  "content_id": null,
  "creator_id": null,
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### RQ10 — `malformed`

*Targeting:* body is form-encoded, not JSON

```json
{
  "id": "RQ10",
  "status": 429,
  "content_id": null,
  "creator_id": null,
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### RQ11 — `malformed`

*Targeting:* body is JSON claiming to be plain text

```json
{
  "id": "RQ11",
  "status": 429,
  "content_id": null,
  "creator_id": null,
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### RQ12 — `malformed`

*Targeting:* deeply nested JSON

```json
{
  "id": "RQ12",
  "status": 400,
  "content_id": null,
  "creator_id": "attacker_RQ12",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### FL01_01 — `flood_same_creator`

*Targeting:* 20 rapid submissions from one creator

```json
{
  "id": "FL01_01",
  "status": 200,
  "content_id": "f17dfd3e-93ac-470e-88f4-fda655438fc2",
  "creator_id": "attacker_flood",
  "guess": "human",
  "confidence": 0.4714,
  "model_score": 0.0287,
  "style_score": 0.5,
  "label": "We think this was probably written by a person. Our checks found the kind of variety in wording and sentence length that is typical of human writing.",
  "error": null,
  "verdict": ""
}
```

### FL01_02 — `flood_same_creator`

*Targeting:* 20 rapid submissions from one creator

```json
{
  "id": "FL01_02",
  "status": 200,
  "content_id": "4cb23df5-9438-47e1-bef3-a1414db2e85b",
  "creator_id": "attacker_flood",
  "guess": "human",
  "confidence": 0.4714,
  "model_score": 0.0287,
  "style_score": 0.5,
  "label": "We think this was probably written by a person. Our checks found the kind of variety in wording and sentence length that is typical of human writing.",
  "error": null,
  "verdict": ""
}
```

### FL01_03 — `flood_same_creator`

*Targeting:* 20 rapid submissions from one creator

```json
{
  "id": "FL01_03",
  "status": 200,
  "content_id": "47423e9d-185f-4ace-845a-385899ff1e18",
  "creator_id": "attacker_flood",
  "guess": "human",
  "confidence": 0.4714,
  "model_score": 0.0287,
  "style_score": 0.5,
  "label": "We think this was probably written by a person. Our checks found the kind of variety in wording and sentence length that is typical of human writing.",
  "error": null,
  "verdict": ""
}
```

### FL01_04 — `flood_same_creator`

*Targeting:* 20 rapid submissions from one creator

```json
{
  "id": "FL01_04",
  "status": 200,
  "content_id": "edeb5d2e-fde7-4b15-8913-e5251473f671",
  "creator_id": "attacker_flood",
  "guess": "human",
  "confidence": 0.4714,
  "model_score": 0.0287,
  "style_score": 0.5,
  "label": "We think this was probably written by a person. Our checks found the kind of variety in wording and sentence length that is typical of human writing.",
  "error": null,
  "verdict": ""
}
```

### FL01_05 — `flood_same_creator`

*Targeting:* 20 rapid submissions from one creator

```json
{
  "id": "FL01_05",
  "status": 200,
  "content_id": "38070ef4-f3ec-4f10-afb0-2704d6aaec81",
  "creator_id": "attacker_flood",
  "guess": "human",
  "confidence": 0.4714,
  "model_score": 0.0287,
  "style_score": 0.5,
  "label": "We think this was probably written by a person. Our checks found the kind of variety in wording and sentence length that is typical of human writing.",
  "error": null,
  "verdict": ""
}
```

### FL01_06 — `flood_same_creator`

*Targeting:* 20 rapid submissions from one creator

```json
{
  "id": "FL01_06",
  "status": 429,
  "content_id": null,
  "creator_id": "attacker_flood",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### FL01_07 — `flood_same_creator`

*Targeting:* 20 rapid submissions from one creator

```json
{
  "id": "FL01_07",
  "status": 429,
  "content_id": null,
  "creator_id": "attacker_flood",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### FL01_08 — `flood_same_creator`

*Targeting:* 20 rapid submissions from one creator

```json
{
  "id": "FL01_08",
  "status": 429,
  "content_id": null,
  "creator_id": "attacker_flood",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### FL01_09 — `flood_same_creator`

*Targeting:* 20 rapid submissions from one creator

```json
{
  "id": "FL01_09",
  "status": 429,
  "content_id": null,
  "creator_id": "attacker_flood",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### FL01_10 — `flood_same_creator`

*Targeting:* 20 rapid submissions from one creator

```json
{
  "id": "FL01_10",
  "status": 429,
  "content_id": null,
  "creator_id": "attacker_flood",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### FL01_11 — `flood_same_creator`

*Targeting:* 20 rapid submissions from one creator

```json
{
  "id": "FL01_11",
  "status": 429,
  "content_id": null,
  "creator_id": "attacker_flood",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### FL01_12 — `flood_same_creator`

*Targeting:* 20 rapid submissions from one creator

```json
{
  "id": "FL01_12",
  "status": 429,
  "content_id": null,
  "creator_id": "attacker_flood",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```
