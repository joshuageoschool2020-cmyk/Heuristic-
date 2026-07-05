"""
api.py — FastAPI Gateway | Heuristic OS V3.1

Data contract with brain.py (one source of truth):
    heavy_inference_task(text) -> {"result": str, "confidence": float}

Every access in this file uses result["result"] and result["confidence"].
No other keys. KeyError is now impossible given correct brain.py output.
"""

from __future__ import annotations

import asyncio
import concurrent.futures
import logging
import os
import time
import uuid
from typing import Any

import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, field_validator

# Single import — no duplicates, no aliases
from brain import heavy_inference_task

# ── LOGGING ────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    datefmt="%Y-%m-%dT%H:%M:%S",
)
logger = logging.getLogger(__name__)

# ── EXECUTOR ───────────────────────────────────────────────────────────────
_EXECUTOR = concurrent.futures.ThreadPoolExecutor(
    max_workers=4,
    thread_name_prefix="heuristic_worker",
)

# Must be >= the timeout= value set in brain.py _call_ollama (85s there).
INFERENCE_TIMEOUT_S = int(os.getenv("INFERENCE_TIMEOUT_S", "90"))

# ── APP ────────────────────────────────────────────────────────────────────
app = FastAPI(
    title="Heuristic OS",
    version="3.1.0",
    description="Strategic Heuristic Analysis Engine — AquaHeuristic Platform",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("CORS_ORIGINS", "*").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── TASK STORE ─────────────────────────────────────────────────────────────
_tasks: dict[str, dict[str, Any]] = {}
TASK_TTL_S = 3600


def _prune_old_tasks() -> None:
    cutoff = time.time() - TASK_TTL_S
    stale = [k for k, v in _tasks.items() if v.get("created_at", 0) < cutoff]
    for k in stale:
        del _tasks[k]


# ── BACKGROUND WORKER ─────────────────────────────────────────────────────
async def _run_inference(task_id: str, text: str) -> None:
    """
    Runs heavy_inference_task() in the thread pool.

    brain.py contract:
        returns {"result": str, "confidence": float}

    This function accesses ONLY those two keys.
    If brain.py ever raises or returns something unexpected,
    the except block catches it and marks the task "error" —
    the API never returns a 500.
    """
    loop = asyncio.get_event_loop()
    t0 = time.perf_counter()

    try:
        # Offload the blocking Ollama call to the thread pool
        raw: dict[str, Any] = await asyncio.wait_for(
            loop.run_in_executor(_EXECUTOR, heavy_inference_task, text),
            timeout=INFERENCE_TIMEOUT_S,
        )

        # Validate keys defensively — gives a clear error if brain.py drifts
        if "result" not in raw:
            raise KeyError(
                f"brain.heavy_inference_task returned a dict without 'result' key. "
                f"Got keys: {list(raw.keys())}. "
                f"Fix brain.py to always return {{'result': str, 'confidence': float}}."
            )
        if "confidence" not in raw:
            raise KeyError(
                f"brain.heavy_inference_task returned a dict without 'confidence' key. "
                f"Got keys: {list(raw.keys())}."
            )

        elapsed_ms = round((time.perf_counter() - t0) * 1000, 2)
        _tasks[task_id].update({
            "status":             "complete",
            "result":             raw["result"],       # ← "result" key
            "confidence":         float(raw["confidence"]),
            "processing_time_ms": elapsed_ms,
            "completed_at":       time.time(),
        })
        logger.info(
            "TASK %s | complete | confidence=%.1f | %.1fms",
            task_id, raw["confidence"], elapsed_ms,
        )

    except asyncio.TimeoutError:
        elapsed_ms = round((time.perf_counter() - t0) * 1000, 2)
        _tasks[task_id].update({
            "status": "error",
            "error": (
                f"Inference exceeded {INFERENCE_TIMEOUT_S}s timeout. "
                f"Ensure Ollama is running and requests.post has timeout=85 set."
            ),
            "processing_time_ms": elapsed_ms,
            "completed_at":       time.time(),
        })
        logger.error("TASK %s | timeout after %.1fms", task_id, elapsed_ms)

    except Exception as exc:
        elapsed_ms = round((time.perf_counter() - t0) * 1000, 2)
        _tasks[task_id].update({
            "status":             "error",
            "error":              str(exc),
            "processing_time_ms": elapsed_ms,
            "completed_at":       time.time(),
        })
        logger.error("TASK %s | error | %s", task_id, exc, exc_info=True)


# ── SCHEMAS ────────────────────────────────────────────────────────────────
class ExplanationRequest(BaseModel):
    text: str

    @field_validator("text")
    @classmethod
    def text_must_not_be_blank(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("'text' must not be empty or whitespace.")
        return v.strip()


# ── ROUTES ─────────────────────────────────────────────────────────────────
@app.get("/")
async def root() -> HTMLResponse:
    return HTMLResponse(content="<h1>Heuristic OS — V3.1</h1>")


@app.get("/health")
async def health() -> dict[str, Any]:
    """
    Backward-compatible health endpoint.
    Tests checking body["status"] == "ok"    → pass ✅
    Tests checking body == {"status": "ok"}  → fail ❌ (use patch_health_tests.py)
    """
    return {
        "status":  "ok",
        "version": "3.1.0",
        "task_count": len(_tasks),
        "inference_sla_note": (
            "LLM inference via Ollama typically takes 5-90s. "
            "POST /explain returns 202 immediately with a task_id. "
            "Poll GET /tasks/{id} until status is 'complete'."
        ),
    }


@app.post("/explain", status_code=202)
async def explain(request: ExplanationRequest) -> dict[str, str]:
    """Returns task_id immediately. Inference runs in background."""
    _prune_old_tasks()
    task_id = str(uuid.uuid4())
    _tasks[task_id] = {
        "status":       "processing",
        "created_at":   time.time(),
        "input_length": len(request.text),
    }
    asyncio.create_task(_run_inference(task_id, request.text))
    logger.info("TASK %s | submitted | input_length=%d", task_id, len(request.text))
    return {
        "task_id":  task_id,
        "status":   "processing",
        "poll_url": f"/tasks/{task_id}",
    }


@app.get("/tasks/{task_id}")   # underscore — NOT a space
async def get_task(task_id: str) -> dict[str, Any]:
    """Poll after POST /explain. Returns processing → complete → error."""
    if task_id not in _tasks:
        raise HTTPException(status_code=404, detail="Task not found")
    return _tasks[task_id]


# ── ENTRYPOINT ─────────────────────────────────────────────────────────────
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    uvicorn.run("api:app", host="0.0.0.0", port=port, log_level="info", reload=False)