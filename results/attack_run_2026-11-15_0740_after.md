# Attack run — after

- Produced by: `run_attacks.py::main`
- Service: `app.py::submit`
- 56 attacks · 2026-11-15 07:40
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
| EV01 | evasion | signal two: typos raise word variety | 200 | `d46c4bfc-4a94-409f-be6c-6bcbee05098b` | human | 0.319 |  |
| EV02 | evasion | signal two: broken-up sentences raise length spread | 200 | `512b1ded-3f8a-4553-9843-1f358fea6810` | unsure | 0.211 |  |
| EV03 | evasion | signal two: a pasted quotation changes the shape | 200 | `d1cebb32-fe9e-4e8a-9b00-7430557be31c` | unsure | 0.034 |  |
| EV04 | evasion | signal one: unusual words raise perplexity | 200 | `f2218989-2c9b-42ab-99ee-2045d6a79ac8` | unsure | 0.106 |  |
| EV05 | evasion | both signals: heavy human editing pass | 200 | `3af19456-5337-4fad-8902-2ed7277cb879` | human | 0.430 |  |
| EV06 | evasion | signal two: one very long sentence and one very short | 200 | `6abad488-b8d3-447f-bf99-fb49209a450a` | unsure | 0.166 |  |
| EV07 | evasion | signal two: padding with punctuation | 200 | `b15acf12-507c-41f7-ac17-b1424dab2f41` | unsure | 0.086 |  |
| EV08 | evasion | signal one: text below the token window | 200 | `08cbc9ba-4a70-4371-9665-cb7aad51a742` | unsure | 0.264 |  |
| EV09 | evasion | both: AI text with a human opening paragraph bolted on | 200 | `0e65cb49-ff99-4a49-88f8-512ef6f40d59` | unsure | 0.056 |  |
| EV10 | evasion | signal two: repeated stanza structure | 200 | `5699fd6e-1f57-47d1-9898-cdea7f7d288a` | ai | 0.758 |  |
| FP01 | false_positive | plain, clear human writing with no flourishes | 200 | `dbebcbac-d4ce-4393-9373-d6d7f95040c1` | unsure | 0.118 |  |
| FP02 | false_positive | human writing in a formal register | 200 | `db7d2e70-208d-4b6e-ab87-bd35c1e861f0` | unsure | 0.369 |  |
| FP03 | false_positive | a non-native English speaker writing carefully | 200 | `0fd1cd0c-4fe5-4da2-8c7e-8fbeaf999746` | unsure | 0.395 |  |
| FP04 | false_positive | a student essay written to a rubric | 200 | `df4d5779-2200-44fa-bbe4-c1afcfc0f5d8` | unsure | 0.321 |  |
| FP05 | false_positive | technical documentation written by a person | 200 | `7be6a23d-0c93-472a-8b09-e2d1c42e9613` | unsure | 0.477 |  |
| FP06 | false_positive | a person imitating a formal template | 200 | `a553613c-c99d-4f1b-8cd6-5ae8cd4c5095` | unsure | 0.335 |  |
| FP07 | false_positive | human writing that repeats a phrase deliberately | 200 | `70f75fb6-b764-4376-9498-649df4b9e595` | unsure | 0.385 |  |
| FP08 | false_positive | very short genuine human submission | 200 | `a605beac-d894-4762-841a-bf7d435feb1e` | unsure | 0.178 |  |
| PI01 | prompt_injection | instruction to ignore the check | 200 | `1831de76-5297-4e3c-814b-e30fd3c174c7` | unsure | 0.260 |  |
| PI02 | prompt_injection | instruction disguised as a system message | 200 | `76ce3d6d-dd8d-45c8-a8e4-5f2200824c32` | human | 0.572 |  |
| PI03 | prompt_injection | instruction wrapped in the writer's voice | 200 | `31933391-874c-4108-8bc5-8019e28fce11` | unsure | 0.021 |  |
| PI04 | prompt_injection | attempt to make the label text hostile | 200 | `37698cef-af80-40c3-b574-5577e7644bde` | unsure | 0.152 |  |
| PI05 | prompt_injection | attempt to inject into the audit log | 200 | `84b026a5-493a-4ae1-8ae5-08ac590b5613` | unsure | 0.175 |  |
| PI06 | prompt_injection | instruction plus real human text | 200 | `81bef9b4-1d6a-4ad6-afa0-eeb4ab820c0d` | unsure | 0.069 |  |
| MF01 | malformed | text is only whitespace | 400 | `—` | — | — |  |
| MF02 | malformed | text is a single character | 500 | `—` | — | — | BROKE |
| MF03 | malformed | text is control characters | 200 | `93700cd0-a262-45e5-8500-2b751aae963d` | human | 0.500 |  |
| MF04 | malformed | text is only punctuation | 200 | `5ea71361-8a02-41f7-98fd-a7159d43dbf7` | human | 0.489 |  |
| MF05 | malformed | text is a very long single word | 200 | `f23e239d-06af-40c1-a24e-1457ff4a2086` | unsure | 0.480 |  |
| MF06 | malformed | text is emoji only | 200 | `5aa54f55-3759-4de2-ac6a-4254e2580ceb` | unsure | 0.480 |  |
| MF07 | malformed | text is right-to-left script | 200 | `e45bad74-f850-42cf-a4aa-6bec2df1c1fb` | unsure | 0.406 |  |
| MF08 | malformed | text is 60,000 characters | 200 | `f36726aa-1000-479a-9f50-a3286939e9c0` | ai | 0.721 |  |
| RQ01 | malformed | no text field at all | 400 | `—` | — | — |  |
| RQ02 | malformed | no creator_id | 400 | `—` | — | — |  |
| RQ03 | malformed | text is a number | 400 | `—` | — | — |  |
| RQ04 | malformed | text is a list | 400 | `—` | — | — |  |
| RQ05 | malformed | text is null | 400 | `—` | — | — |  |
| RQ06 | malformed | creator_id is an object | 400 | `—` | — | — |  |
| RQ07 | malformed | body is a JSON array, not an object | 500 | `—` | — | — | BROKE |
| RQ08 | malformed | body is unparseable JSON | 400 | `—` | — | — |  |
| RQ09 | malformed | body is empty | 400 | `—` | — | — |  |
| RQ10 | malformed | body is form-encoded, not JSON | 429 | `—` | — | — |  |
| RQ11 | malformed | body is JSON claiming to be plain text | 429 | `—` | — | — |  |
| RQ12 | malformed | deeply nested JSON | 400 | `—` | — | — |  |
| FL01_01 | flood_same_creator | 20 rapid submissions from one creator | 200 | `30dd99db-acf5-4ec1-a23e-b1e2221b0d17` | human | 0.471 |  |
| FL01_02 | flood_same_creator | 20 rapid submissions from one creator | 200 | `a70f0a9a-ecaf-479e-9a7d-b884a3935767` | human | 0.471 |  |
| FL01_03 | flood_same_creator | 20 rapid submissions from one creator | 200 | `56591150-5b64-44b8-9859-9f1b28f22e80` | human | 0.471 |  |
| FL01_04 | flood_same_creator | 20 rapid submissions from one creator | 200 | `2e55e1bd-7d84-448b-8c32-c958b9074c99` | human | 0.471 |  |
| FL01_05 | flood_same_creator | 20 rapid submissions from one creator | 200 | `cb0208ec-da26-417f-877d-18dd78014240` | human | 0.471 |  |
| FL01_06 | flood_same_creator | 20 rapid submissions from one creator | 429 | `—` | — | — |  |
| FL01_07 | flood_same_creator | 20 rapid submissions from one creator | 429 | `—` | — | — |  |
| FL01_08 | flood_same_creator | 20 rapid submissions from one creator | 429 | `—` | — | — |  |
| FL01_09 | flood_same_creator | 20 rapid submissions from one creator | 429 | `—` | — | — |  |
| FL01_10 | flood_same_creator | 20 rapid submissions from one creator | 429 | `—` | — | — |  |
| FL01_11 | flood_same_creator | 20 rapid submissions from one creator | 429 | `—` | — | — |  |
| FL01_12 | flood_same_creator | 20 rapid submissions from one creator | 429 | `—` | — | — |  |

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
  "content_id": "d46c4bfc-4a94-409f-be6c-6bcbee05098b",
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
  "content_id": "512b1ded-3f8a-4553-9843-1f358fea6810",
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
  "content_id": "d1cebb32-fe9e-4e8a-9b00-7430557be31c",
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
  "content_id": "f2218989-2c9b-42ab-99ee-2045d6a79ac8",
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
  "content_id": "3af19456-5337-4fad-8902-2ed7277cb879",
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
  "content_id": "6abad488-b8d3-447f-bf99-fb49209a450a",
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
  "content_id": "b15acf12-507c-41f7-ac17-b1424dab2f41",
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
  "content_id": "08cbc9ba-4a70-4371-9665-cb7aad51a742",
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
  "content_id": "0e65cb49-ff99-4a49-88f8-512ef6f40d59",
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
  "content_id": "5699fd6e-1f57-47d1-9898-cdea7f7d288a",
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
  "content_id": "dbebcbac-d4ce-4393-9373-d6d7f95040c1",
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
  "content_id": "db7d2e70-208d-4b6e-ab87-bd35c1e861f0",
  "creator_id": "attacker_FP02",
  "guess": "unsure",
  "confidence": 0.3686,
  "model_score": 0.7387,
  "style_score": 0.6299,
  "label": "We can't tell whether this was written by a person or with help from AI. Our checks gave mixed results, which happens often with genuine human writing, especially plain or formal styles. This is not an accusation, and it shouldn't be treated as evidence either way.",
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
  "content_id": "0fd1cd0c-4fe5-4da2-8c7e-8fbeaf999746",
  "creator_id": "attacker_FP03",
  "guess": "unsure",
  "confidence": 0.3946,
  "model_score": 0.8051,
  "style_score": 0.5894,
  "label": "We can't tell whether this was written by a person or with help from AI. Our checks gave mixed results, which happens often with genuine human writing, especially plain or formal styles. This is not an accusation, and it shouldn't be treated as evidence either way.",
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
  "content_id": "df4d5779-2200-44fa-bbe4-c1afcfc0f5d8",
  "creator_id": "attacker_FP04",
  "guess": "unsure",
  "confidence": 0.3208,
  "model_score": 0.8329,
  "style_score": 0.488,
  "label": "We can't tell whether this was written by a person or with help from AI. Our checks gave mixed results, which happens often with genuine human writing, especially plain or formal styles. This is not an accusation, and it shouldn't be treated as evidence either way.",
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
  "content_id": "7be6a23d-0c93-472a-8b09-e2d1c42e9613",
  "creator_id": "attacker_FP05",
  "guess": "unsure",
  "confidence": 0.4768,
  "model_score": 0.8005,
  "style_score": 0.6762,
  "label": "We can't tell whether this was written by a person or with help from AI. Our checks gave mixed results, which happens often with genuine human writing, especially plain or formal styles. This is not an accusation, and it shouldn't be treated as evidence either way.",
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
  "content_id": "a553613c-c99d-4f1b-8cd6-5ae8cd4c5095",
  "creator_id": "attacker_FP06",
  "guess": "unsure",
  "confidence": 0.3346,
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
  "content_id": "70f75fb6-b764-4376-9498-649df4b9e595",
  "creator_id": "attacker_FP07",
  "guess": "unsure",
  "confidence": 0.385,
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
  "content_id": "a605beac-d894-4762-841a-bf7d435feb1e",
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
  "content_id": "1831de76-5297-4e3c-814b-e30fd3c174c7",
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
  "content_id": "76ce3d6d-dd8d-45c8-a8e4-5f2200824c32",
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
  "content_id": "31933391-874c-4108-8bc5-8019e28fce11",
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
  "content_id": "37698cef-af80-40c3-b574-5577e7644bde",
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
  "content_id": "84b026a5-493a-4ae1-8ae5-08ac590b5613",
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
  "content_id": "81bef9b4-1d6a-4ad6-afa0-eeb4ab820c0d",
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
  "content_id": "93700cd0-a262-45e5-8500-2b751aae963d",
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
  "content_id": "5ea71361-8a02-41f7-98fd-a7159d43dbf7",
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
  "content_id": "f23e239d-06af-40c1-a24e-1457ff4a2086",
  "creator_id": "attacker_MF05",
  "guess": "unsure",
  "confidence": 0.48,
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
  "content_id": "5aa54f55-3759-4de2-ac6a-4254e2580ceb",
  "creator_id": "attacker_MF06",
  "guess": "unsure",
  "confidence": 0.48,
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
  "content_id": "e45bad74-f850-42cf-a4aa-6bec2df1c1fb",
  "creator_id": "attacker_MF07",
  "guess": "unsure",
  "confidence": 0.4064,
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
  "content_id": "f36726aa-1000-479a-9f50-a3286939e9c0",
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
  "content_id": "30dd99db-acf5-4ec1-a23e-b1e2221b0d17",
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
  "content_id": "a70f0a9a-ecaf-479e-9a7d-b884a3935767",
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
  "content_id": "56591150-5b64-44b8-9859-9f1b28f22e80",
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
  "content_id": "2e55e1bd-7d84-448b-8c32-c958b9074c99",
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
  "content_id": "cb0208ec-da26-417f-877d-18dd78014240",
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
