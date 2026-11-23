#!/usr/bin/env python3
"""
Provenance Guard — the web service.

    python app.py

Then, in another terminal:

    curl -X POST http://127.0.0.1:5000/ping \
      -H "Content-Type: application/json" \
      -d '{"message": "hello"}'

That's the example route. It works right now, before you've written anything.
**Leave it alone** — it's your control. When something breaks later, check that
`/ping` still answers: if it does, the problem is in your handler; if it
doesn't, it's the service itself.

Routes:

    POST /ping        the worked example. Already works. Don't edit it
    POST /submit      ← YOU BUILD THIS (Milestone 3, 4, 5)
    POST /appeal      ← YOU BUILD THIS (Milestone 5)
    GET  /log         the audit log. Already works
    GET  /health      is the service up, and is the model loaded
"""

import re
import time
import uuid

from flask import Flask, g, jsonify, request
from werkzeug.exceptions import HTTPException

import audit
import config
import detector
import scoring
import stylometry

app = Flask(__name__)


# ── Instrumentation (capstone) ────────────────────────────────────────────────
# Every audit entry written while handling a request carries how long that
# request had taken and how much CPU it had burned by the time it was logged.
# The timer is registered here, before the rate limiter attaches its own
# before_request hook, so it starts first and a 429 still gets a duration.

@app.before_request
def _start_timer():
    g.t_wall = time.perf_counter()
    g.t_cpu = time.process_time()


def _timing() -> dict:
    """
    Wall-clock and CPU milliseconds since the request arrived.

    cpu_ms is process CPU time, summed over every thread, so it can exceed
    duration_ms when torch scores on several cores at once. It is only
    meaningful while one request is in flight at a time, which is how
    measure_cost.py drives the service.
    """
    if not hasattr(g, "t_wall"):
        return {"duration_ms": None, "cpu_ms": None}
    return {
        "duration_ms": round((time.perf_counter() - g.t_wall) * 1000, 1),
        "cpu_ms": round((time.process_time() - g.t_cpu) * 1000, 1),
    }


@app.errorhandler(Exception)
def _unhandled(exc):
    """
    A crash still leaves a record, and is still a 500.

    This doesn't turn a bug into a polite 400: the caller gets a 500 and the
    log gets the exception type and message, so a crash is visible in both
    places instead of only in a terminal that's gone by tomorrow. HTTP errors
    (404, 405, 429…) pass straight through to their normal handling.
    """
    if isinstance(exc, HTTPException):
        return exc
    payload = request.get_json(silent=True)
    creator = payload.get("creator_id") if isinstance(payload, dict) else None
    audit.log_rejection(
        creator_id=creator if isinstance(creator, str) else "unknown",
        reason="server_error",
        event="error",
        status="error",
        route=request.path,
        http_status=500,
        error_type=type(exc).__name__,
        error_message=str(exc)[:200],
        **_timing(),
    )
    return jsonify({
        "error": "server_error",
        "message": "Something went wrong on our side. Nothing was scored.",
    }), 500


# ── Rate limiting — UNIT 8 ────────────────────────────────────────────────────
# Off until you turn it on. In unit 8, Milestone 1:
#
#   1. Set RATE_LIMITING_ENABLED = True in config.py (or AI201_RATE_LIMITS=1)
#   2. Choose your numbers there
#   3. Uncomment the @limiter.limit(...) line on /submit below
#
# The order doesn't matter. While limiting is off, that decorator is a no-op
# that quietly does nothing, so uncommenting it early costs you nothing — but
# it also means no 429 until you've done step 1.
#
# The storage backend is preconfigured, which stops Flask-Limiter printing a
# warning on every start. In-memory is right for one laptop and wrong for
# anything real — a restart forgets every count.

class _LimiterOff:
    """
    Stands in for the real limiter while rate limiting is off.

    It makes @limiter.limit(...) a decorator that returns the route
    untouched, so uncommenting the line before you flip the setting is
    harmless instead of a crash on startup.
    """

    def limit(self, *args, **kwargs):
        return lambda view: view


limiter = _LimiterOff()
if config.RATE_LIMITING_ENABLED:
    from flask_limiter import Limiter
    from flask_limiter.util import get_remote_address

    def rate_limit_key():
        """
        Who a request counts against.

        Falling back to the caller's address is the easy version. Unit 8's
        stretch asks about per-creator limits instead — and the difference
        matters: one script can look like a thousand callers, and one household
        can look like one.
        """
        payload = request.get_json(silent=True)
        # A body that parses as JSON but isn't an object — a bare list or
        # string — has no .get. Without this guard the key function raises
        # BEFORE the route runs, and a malformed request becomes a 500 that
        # looks like your handler crashed when your handler never ran.
        if not isinstance(payload, dict):
            return get_remote_address()
        creator = payload.get("creator_id")
        return creator if isinstance(creator, str) and creator.strip() else get_remote_address()

    limiter = Limiter(
        key_func=rate_limit_key,
        app=app,
        storage_uri=config.RATE_LIMIT_STORAGE,
        default_limits=[],
    )

    @app.errorhandler(429)
    def rate_limited(exc):
        """
        A rejected request still leaves a trace.

        ⚠️ An attack that shows up only as an absence is one you'll never find.
        """
        payload = request.get_json(silent=True)
        if not isinstance(payload, dict):
            payload = {}
        audit.log_rejection(
            creator_id=payload.get("creator_id", "unknown"),
            reason="rate_limited",
            limit=str(exc.description),
            route=request.path,
            http_status=429,
            **_timing(),
        )
        return jsonify({
            "error": "rate_limited",
            "message": "Too many submissions. Try again shortly.",
            "limit": str(exc.description),
        }), 429


# ── Input gate helper (capstone) ──────────────────────────────────────────────

_READABLE_WORD = re.compile(r"[A-Za-z]+(?:'[A-Za-z]+)*")


def readable_words(text: str) -> list[str]:
    """
    Runs of Latin letters, with apostrophes allowed inside ("don't").

    This is what the input gate counts. Punctuation, digits, emoji, control
    characters and non-Latin scripts contribute nothing, because neither
    signal can read them.
    """
    return _READABLE_WORD.findall(text)


# Capstone improvement (Milestone 6). The most common words in any English
# sentence: articles, pronouns, prepositions, auxiliaries, conjunctions and a
# few very frequent adverbs. Real English prose of five or more words almost
# always contains at least one. Keyboard mash ("asdf qwer zxcv hjkl uiop"),
# lorem ipsum, and runs of letters in other languages almost never do. That
# makes this a cheap test of "is this English prose?" that doesn't need the
# model, so the gate still runs before GPT-2 loads.
FUNCTION_WORDS = frozenset("""
a an the this that these those
i me my mine we us our ours you your yours he him his she her hers it its
they them their theirs who whom whose which what
am is are was were be been being have has had having do does did doing
will would shall should can could may might must
i'm i've i'll i'd you're you've you'll you'd he's she's it's we're we've
we'll they're they've they'll that's there's what's who's let's
can't won't don't doesn't didn't isn't aren't wasn't weren't haven't
hasn't hadn't wouldn't shouldn't couldn't mustn't
and but or nor so if then than because as until while though although
of at by for with about against between into through during before after
above below to from up down in out on off over under
again further once here there when where why how
all any both each few more most other some such no not only own same too
very just now also
""".split())


def function_word_count(words: list[str]) -> int:
    """How many of the readable words are common English function words."""
    return sum(1 for w in words if w.lower() in FUNCTION_WORDS)


# ── The worked example. Already works. Don't edit. ────────────────────────────

@app.post("/ping")
def ping():
    """
    Everything a route needs, in six lines.

    JSON arrives as a dict. You pull things out of it. You return a dict and
    the framework turns it into a response. That's the whole idea.
    """
    payload = request.get_json(silent=True) or {}
    return jsonify({
        "ok": True,
        "you_sent": payload.get("message"),
        "service": "provenance-guard",
    })


@app.get("/health")
def health():
    """Is the service up, and has the model been downloaded yet?"""
    import detector

    loaded = detector._model is not None
    return jsonify({
        "ok": True,
        "detector_model": config.DETECTOR_MODEL,
        "detector_loaded": loaded,
        "rate_limiting": config.RATE_LIMITING_ENABLED,
        "log_entries": len(audit.read_entries()),
    })


# ── YOU BUILD THIS ────────────────────────────────────────────────────────────

@app.post("/submit")
@limiter.limit(f"{config.RATE_LIMIT_PER_MINUTE}/minute;{config.RATE_LIMIT_PER_DAY}/day")
def submit():
    """
    Take a piece of text, decide about it, log the decision, answer.
    ← TODO — Milestones 3, 4 and 5

    Expects JSON:
        {"text": "...", "creator_id": "..."}

    Should return JSON with, at minimum:
        {"content_id": "...", "guess": "...", "confidence": 0.0, "label": "...",
         "model_score": 0.0, "style_score": 0.0}

    ⚠️ **Both signal scores go in the response, not just the log.** Unit 8's
    `run_attacks.py` and `run_eval.py` read `model_score` and `style_score`
    straight off this response and put them in your reports. Leave them out and
    every row of next unit's evidence says `null` — which is exactly the
    diagnostic you need to name a stage and a mechanism. You do not want to
    find that out after running the attack set.

    ─────────────────────────────────────────────────────────────────────────
    Build it in three passes. Do not skip ahead — the ordering is how you tell
    a broken route from a broken signal.

    **Milestone 3 — the route answers.**
      1. Return a hardcoded response. Confirm `curl` gets it back before you
         add any logic at all.
      2. Then pull `text` and `creator_id` out of the payload.
      3. Then call ONE signal — `detector.model_signal(text)` — and put the
         real number in. Leave confidence and label as placeholders.
      4. Log every submission with `audit.log_decision(...)`. The content_id
         matters: `/appeal` needs it, and a student who skips it rebuilds this
         whole flow later.

    **Milestone 4 — the second signal and the score.**
      5. Add `stylometry.style_signal(text)`.
      6. Combine them with `scoring.combine_signals(...)`.
      7. Log BOTH signal scores alongside the combined one, and put them in the
         response too. Next unit you can't diagnose anything without them.

    **Milestone 5 — the label.**
      8. `scoring.score_to_label(...)` and put the real label in the response.

    ─────────────────────────────────────────────────────────────────────────
    Worth deciding early, because unit 8's attack set will decide it for you:
    what should this do when `text` is missing, empty, or enormous? A crash on
    a malformed input is one of the most common real failures there is.
    """
    payload = request.get_json(silent=True)

    def _reject(creator: str, reason: str, message: str, **fields):
        """Log a refused request with its timing, and answer 400."""
        audit.log_rejection(
            creator_id=creator,
            reason=reason,
            route=request.path,
            http_status=400,
            **fields,
            **_timing(),
        )
        return jsonify({"error": "invalid_request", "message": message}), 400

    # Capstone input gate, part 1: the body has to be a JSON object. A JSON
    # array (RQ07) used to reach payload.get() and crash with a 500 that left
    # nothing in the audit log.
    if payload is not None and not isinstance(payload, dict):
        return _reject(
            "unknown", "body_not_object",
            "The request body must be a JSON object with 'text' and "
            "'creator_id'.",
            body_type=type(payload).__name__,
        )
    payload = payload or {}

    text = payload.get("text")
    creator_id = payload.get("creator_id")

    # Invalid input is refused before any scoring: no label, no decision logged.
    if not isinstance(text, str) or not text.strip():
        return _reject(
            creator_id if isinstance(creator_id, str) else "unknown",
            "missing_text",
            "'text' is required and must be non-empty.",
            text_type=type(text).__name__,
        )
    if not isinstance(creator_id, str) or not creator_id.strip():
        return _reject(
            "unknown", "missing_creator_id", "'creator_id' is required.",
            text_chars=len(text),
        )

    # Capstone input gate, part 2: there has to be enough English prose for
    # the signals to read. Before this, one character (MF02) crashed with a
    # 500, and control characters, punctuation, one giant word, emoji and
    # right-to-left script (MF03–MF07) all got a label they had no basis for.
    words = readable_words(text)
    word_count = len(words)
    if word_count < config.MIN_READABLE_WORDS:
        return _reject(
            creator_id, "too_few_readable_words",
            f"We could only find {word_count} readable English word(s) in "
            f"this text. This service checks English prose of at least "
            f"{config.MIN_READABLE_WORDS} words, so nothing was scored and "
            "no label was given.",
            readable_words=word_count,
            text_chars=len(text),
            text_preview=text[:60],
        )

    # Capstone improvement (Milestone 6): enough letter-runs isn't enough. The
    # first trials showed keyboard mash ("asdf qwer zxcv hjkl uiop") has
    # exactly 5 of them, so it passed, loaded GPT-2 and was labelled "human".
    # Require at least MIN_FUNCTION_WORDS common English function words.
    fw_count = function_word_count(words)
    if fw_count < config.MIN_FUNCTION_WORDS:
        return _reject(
            creator_id, "not_english_prose",
            "This doesn't look like English sentences: none of the common "
            "words English writing almost always uses (like 'the', 'is', "
            "'on' or 'I') appear in it. This service checks English prose, "
            "so nothing was scored and no label was given.",
            readable_words=word_count,
            function_words=fw_count,
            text_chars=len(text),
            text_preview=text[:60],
        )

    content_id = str(uuid.uuid4())
    # cold_start: the first scored request loads GPT-2 into memory, which
    # dominates its duration. Recorded so warm and cold runs never get averaged
    # together by accident.
    cold_start = detector._model is None
    t0 = time.perf_counter()
    model_score = detector.model_signal(text)
    t1 = time.perf_counter()
    style_score = stylometry.style_signal(text)
    t2 = time.perf_counter()
    combined_score = scoring.combine_signals(model_score, style_score)
    guess, label = scoring.score_to_label(combined_score)
    # Confidence: how far the score sits from the 0.5 midpoint, rescaled to
    # 0–1. 0.0 = no lean either way, 1.0 = as far toward one end as possible.
    confidence = round(abs(combined_score - 0.5) * 2, 4)

    audit.log_decision(
        content_id=content_id,
        creator_id=creator_id,
        guess=guess,
        model_score=model_score,
        style_score=style_score,
        combined_score=combined_score,
        label=label,
        status="decided",
        event="decided",
        route=request.path,
        http_status=200,
        text_chars=len(text),
        readable_words=word_count,
        text_preview=text[:60],
        cold_start=cold_start,
        model_ms=round((t1 - t0) * 1000, 1),
        style_ms=round((t2 - t1) * 1000, 1),
        **_timing(),
    )

    return jsonify({
        "content_id": content_id,
        "creator_id": creator_id,
        "guess": guess,
        "confidence": confidence,
        "label": label,
        "model_score": model_score,
        "style_score": style_score,
        "combined_score": combined_score,
    }), 200


@app.post("/appeal")
def appeal():
    """
    A writer says you got it wrong. ← TODO — Milestone 5

    Expects JSON:
        {"content_id": "...", "reasoning": "..."}

    Should:
      1. Check the content_id actually exists — `audit.entries_for(id)` tells
         you. A typo here fails silently and looks like a broken endpoint,
         which is the single most common way this milestone eats an hour.
      2. Record the appeal with `audit.log_appeal(...)`, which moves the item
         to `under_review`.
      3. Confirm to the writer. No automatic re-checking needed.

    This is the smallest endpoint in the project and the one that matters most
    to the person on the other end. It's the only thing standing between a
    wrong accusation and nothing at all.
    """
    payload = request.get_json(silent=True) or {}

    content_id = str(payload.get("content_id") or "").strip()
    reasoning = str(payload.get("reasoning") or "").strip()

    if not content_id or not reasoning:
        return jsonify({
            "error": "invalid_request",
            "message": "Both 'content_id' and 'reasoning' are required.",
        }), 400

    # 1. The content_id must belong to a real earlier decision.
    history = audit.entries_for(content_id)
    original = next((e for e in history if e.get("status") == "decided"), None)
    if original is None:
        return jsonify({
            "error": "not_found",
            "message": f"No submission found with content_id '{content_id}'.",
        }), 404

    # 2. Append the appeal next to the original decision (status -> under_review).
    audit.log_appeal(
        content_id=content_id,
        creator_id=original.get("creator_id", "unknown"),
        reasoning=reasoning,
    )

    # 3. Confirm to the writer.
    return jsonify({
        "content_id": content_id,
        "status": "under_review",
        "message": "Appeal recorded.",
    }), 200


# ── Already works ─────────────────────────────────────────────────────────────

@app.get("/log")
def get_log():
    """
    The audit log, most recent last.

        curl "http://127.0.0.1:5000/log?limit=10"

    You need this in unit 8 to paste entries into your README, and you need it
    now to see whether your logging is actually working.
    """
    limit = request.args.get("limit", type=int)
    entries = audit.read_entries(limit=limit)
    return jsonify({"count": len(entries), "entries": entries})


def main():
    print(f"Provenance Guard on http://{config.HOST}:{config.PORT}")
    print(f"  detector model:  {config.DETECTOR_MODEL}")
    print(f"  rate limiting:   {'ON' if config.RATE_LIMITING_ENABLED else 'off (unit 8)'}")
    print(f"  audit log:       {config.AUDIT_LOG}")
    print()
    print("Check it's alive:")
    print(f'  curl -X POST http://{config.HOST}:{config.PORT}/ping \\')
    print('    -H "Content-Type: application/json" \\')
    print("    -d '{\"message\": \"hello\"}'")
    print()
    # debug=True hands out an interactive debugger, so it's local-only — see config.py
    app.run(host=config.HOST, port=config.PORT, debug=config.DEBUG)


if __name__ == "__main__":
    main()
