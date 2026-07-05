"""
brain.py — Heuristic Core Engine | Heuristic OS V3.1

Contract (never changes):
    heavy_inference_task(text: str) -> {"result": str, "confidence": float}

The key is ALWAYS "result". api.py reads result["result"] and
result["confidence"]. Nothing else. No TypedDict aliases, no "text" key.
"""

from __future__ import annotations

import json
import logging
import time
from contextlib import contextmanager

logger = logging.getLogger(__name__)


# ── PROFILING HELPER ──────────────────────────────────────────────────────
@contextmanager
def _section(label: str):
    start = time.perf_counter()
    yield
    logger.info("PROFILE | %-30s | %8.1f ms", label, (time.perf_counter() - start) * 1000)


# ── PUBLIC CONTRACT ───────────────────────────────────────────────────────
def heavy_inference_task(text: str) -> dict[str, object]:
    """
    Runs heuristic analysis on `text` and returns:
        {
            "result":     str,    # formatted heuristic report
            "confidence": float,  # 0.0 – 100.0
        }

    Raises:
        ValueError  — if input is empty or whitespace-only
        RuntimeError — if the model returns unparseable output
    """
    if not text or not text.strip():
        raise ValueError("Input text must not be empty.")

    with _section("prompt_construction"):
        prompt = _build_prompt(text)

    with _section("ollama_http_round_trip"):
        raw_output = _call_ollama(prompt)

    with _section("json_extraction"):
        parsed = _extract_json(raw_output)

    with _section("post_processing"):
        result_text, confidence = _format_output(parsed, text)

    return {
        "result":     result_text,   # ← always "result", never "text"
        "confidence": confidence,
    }


# ── INTERNAL HELPERS ──────────────────────────────────────────────────────
def _build_prompt(text: str) -> str:
    return f"""You are a heuristic analysis engine. Analyze the concept below.
Return ONLY valid JSON. No markdown, no explanation, no preamble.

CONCEPT: {text}

Required JSON schema:
{{
  "CONCEPT": "<concept name>",
  "DEPTH": "STRATEGIC_ANALYSIS",
  "FIRST_PRINCIPLE": "<one sentence>",
  "FRICTION_POINTS": "<one sentence>",
  "HEURISTIC_SYNTHESIS": "<one sentence>",
  "STATUS": "VALIDATED",
  "CONFIDENCE_METRIC": <float 0-100>
}}"""


def _call_ollama(prompt: str) -> str:
    """
    Replace the body of this function with your real Ollama call.
    The timeout= parameter is CRITICAL — without it, requests.post
    blocks forever if Ollama stalls, and asyncio.wait_for cannot
    cancel it (it can only cancel the coroutine, not the thread).
    """
    try:
        import requests  # only imported when actually calling Ollama

        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model":   "llama3",
                "prompt":  prompt,
                "stream":  False,
                "options": {"temperature": 0.0, "seed": 42},
            },
            timeout=85,   # ← REQUIRED: matches INFERENCE_TIMEOUT_S - 5s buffer
        )
        response.raise_for_status()
        return response.json()["response"]

    except Exception as exc:
        # Fallback so tests can run without a live Ollama instance.
        # Remove this block in production.
        logger.warning("Ollama unavailable (%s) — using fallback stub", exc)
        return json.dumps({
            "CONCEPT":              text_from_prompt(prompt),
            "DEPTH":                "STRATEGIC_ANALYSIS",
            "FIRST_PRINCIPLE":      "Fallback — Ollama not available.",
            "FRICTION_POINTS":      "Fallback — Ollama not available.",
            "HEURISTIC_SYNTHESIS":  "Fallback — Ollama not available.",
            "STATUS":               "VALIDATED",
            "CONFIDENCE_METRIC":    50.0,
        })


def text_from_prompt(prompt: str) -> str:
    """Extract CONCEPT value from the prompt for fallback labelling."""
    for line in prompt.splitlines():
        if line.startswith("CONCEPT:"):
            return line.split(":", 1)[1].strip()[:40].upper()
    return "UNKNOWN"


def _extract_json(raw: str) -> dict:
    """
    Parse model output to JSON.
    Strips markdown fences defensively — models often add them despite
    explicit instructions not to.
    """
    cleaned = raw.strip()
    if cleaned.startswith("```"):
        lines = cleaned.splitlines()
        cleaned = "\n".join(
            ln for ln in lines
            if not ln.strip().startswith("```")
        ).strip()

    try:
        return json.loads(cleaned)
    except json.JSONDecodeError as exc:
        raise RuntimeError(
            f"Model returned non-JSON output. "
            f"Tighten your system prompt to forbid markdown fences. "
            f"First 200 chars of raw output: {raw[:200]!r}"
        ) from exc


def _format_output(data: dict, original_text: str) -> tuple[str, float]:
    """Format the parsed JSON into the heuristic report string and extract confidence."""
    # Confidence — normalise to 0-100 float
    raw_conf = data.get("CONFIDENCE_METRIC", 0)
    try:
        confidence = float(str(raw_conf).replace("%", "").strip())
    except (ValueError, TypeError):
        confidence = 0.0
    confidence = max(0.0, min(100.0, confidence))

    concept = data.get("CONCEPT", original_text[:40].upper())

    report = (
        f"[SYSTEM_HEURISTIC_CORE]\n"
        f"{'─' * 50}\n"
        f"CONCEPT   : {concept}\n"
        f"DEPTH     : {data.get('DEPTH', 'STRATEGIC_ANALYSIS')}\n"
        f"{'─' * 50}\n"
        f"1. FIRST_PRINCIPLE     : {data.get('FIRST_PRINCIPLE', '—')}\n"
        f"2. FRICTION_POINTS     : {data.get('FRICTION_POINTS', '—')}\n"
        f"3. HEURISTIC_SYNTHESIS : {data.get('HEURISTIC_SYNTHESIS', '—')}\n"
        f"{'─' * 50}\n"
        f"STATUS             : [{data.get('STATUS', 'VALIDATED')}]\n"
        f"CONFIDENCE_METRIC  : {confidence:.1f}%\n"
    )

    return report, confidence