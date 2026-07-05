"""
test_performance.py
Performance and async-pattern tests for the Task ID architecture.

The old assertion   assert elapsed < 2.0, "API too slow!"
was wrong because it measured total LLM inference time, not submission time.

Correct assertions after the Task ID refactor:
  ✅  POST /explain returns 202 in < SUBMISSION_SLA_MS     (fast)
  ✅  GET  /tasks/{id} returns 200 in < POLL_SLA_MS        (fast)
  ✅  Status reaches "complete" within TOTAL_TIMEOUT_S     (documented, not asserted as "fast")
  ✅  Concurrent submissions don't block each other         (proves run_in_executor is working)

Run:
    pytest test_performance.py -v
"""

from __future__ import annotations

import time
import uuid
import concurrent.futures

import pytest
from fastapi.testclient import TestClient

from api import app

client = TestClient(app, raise_server_exceptions=False)

# ── SLA CONSTANTS ──────────────────────────────────────────────────────────
# How fast the initial 202 Accepted must arrive.
# This is the only thing you should still assert as "fast."
SUBMISSION_SLA_MS = 500

# How fast a single poll round-trip must be (no inference, just dict lookup).
POLL_SLA_MS = 100

# How long to wait for the full result before giving up in tests.
# Set to your realistic worst-case Ollama time. Not a "fast" assertion.
TOTAL_TIMEOUT_S = 240

# How long to sleep between poll attempts.
POLL_INTERVAL_S = 1.0


def poll_until_complete(task_id: str, timeout: float = TOTAL_TIMEOUT_S) -> dict:
    """
    Poll GET /tasks/{task_id} until status is 'complete' or 'error'.
    Raises TimeoutError if the task doesn't finish within timeout seconds.
    Returns the final task payload.
    """
    deadline = time.time() + timeout
    while time.time() < deadline:
        poll_start = time.perf_counter()
        res = client.get(f"/tasks/{task_id}")
        poll_ms = (time.perf_counter() - poll_start) * 1000

        assert res.status_code == 200, f"Poll returned {res.status_code}"
        assert poll_ms < POLL_SLA_MS, (
            f"Poll round-trip took {poll_ms:.1f}ms — exceeds {POLL_SLA_MS}ms. "
            f"The task store lookup should be near-instant; check for blocking code "
            f"in GET /tasks/{{id}}."
        )

        data = res.json()
        if data["status"] in ("complete", "error"):
            return data

        time.sleep(POLL_INTERVAL_S)

    raise TimeoutError(
        f"Task {task_id} did not complete within {timeout}s. "
        f"This is a timeout assertion, not a speed assertion — "
        f"increase TOTAL_TIMEOUT_S if your hardware is slower."
    )


# ── 1. SUBMISSION IS FAST ─────────────────────────────────────────────────
@pytest.mark.integration
def test_submission_returns_202_quickly():
    """
    The critical replacement for the old 2-second assertion.
    POST /explain must return 202 + task_id immediately — before inference starts.
    """
    start = time.perf_counter()
    res = client.post("/explain", json={"text": "test submission latency"})
    elapsed_ms = (time.perf_counter() - start) * 1000

    assert res.status_code == 202, f"Expected 202, got {res.status_code}"
    assert elapsed_ms < SUBMISSION_SLA_MS, (
        f"Submission took {elapsed_ms:.1f}ms — exceeds {SUBMISSION_SLA_MS}ms SLA. "
        f"POST /explain should return immediately without waiting for inference. "
        f"Check that asyncio.create_task() is being called correctly and that "
        f"no blocking code runs before the return statement."
    )

    body = res.json()
    assert "task_id" in body
    assert body["status"] == "processing"
    assert "poll_url" in body

@pytest.mark.integration
def test_submission_response_schema():
    res = client.post("/explain", json={"text": "schema check"})
    assert res.status_code == 202
    body = res.json()
    assert set(body.keys()) == {"task_id", "status", "poll_url"}
    assert isinstance(body["task_id"], str) and len(body["task_id"]) == 36  # UUID format
    assert body["status"] == "processing"
    assert body["poll_url"] == f"/tasks/{body['task_id']}"


# ── 2. POLLING IS FAST ────────────────────────────────────────────────────
@pytest.mark.integration
def test_poll_endpoint_is_fast_during_processing():
    """
    While the task is still processing, polling should return instantly.
    This confirms the poll endpoint does no work beyond a dict lookup.
    """
    res = client.post("/explain", json={"text": "poll speed check"})
    task_id = res.json()["task_id"]

    # Poll immediately — task should still be processing (Ollama takes seconds)
    for _ in range(3):
        start = time.perf_counter()
        poll_res = client.get(f"/tasks/{task_id}")
        elapsed_ms = (time.perf_counter() - start) * 1000

        assert poll_res.status_code == 200
        assert elapsed_ms < POLL_SLA_MS, (
            f"Poll took {elapsed_ms:.1f}ms during processing state — "
            f"should be a near-instant dict lookup."
        )


@pytest.mark.integration
def test_unknown_task_id_returns_404():
    res = client.get(f"/tasks/{uuid.uuid4()}")
    assert res.status_code == 404


# ── 3. FULL ROUND TRIP (documented, not speed-asserted) ───────────────────
@pytest.mark.integration
def test_full_inference_completes_and_returns_valid_payload():
    """
    Submits a real request and polls until complete.
    Does NOT assert a speed SLA on total inference time — Ollama on CPU
    can take 16-83 seconds as you've observed, and that's a hardware
    constraint, not a code bug.

    What this test does assert:
      - The result eventually arrives
      - The schema is correct when it does
      - confidence is in a valid range
    """
    res = client.post("/explain", json={"text": "evaluate risk in a leveraged buyout"})
    assert res.status_code == 202
    task_id = res.json()["task_id"]

    result = poll_until_complete(task_id)

    assert result["status"] == "complete", (
        f"Task ended with status {result['status']!r}. "
        f"Error: {result.get('error', 'none')}"
    )
    assert isinstance(result.get("result"), str) and result["result"].strip()
    assert isinstance(result.get("confidence"), (int, float))
    assert 0.0 <= result["confidence"] <= 100.0
    assert isinstance(result.get("processing_time_ms"), (int, float))

    # Log the actual time so you have a baseline for real hardware
    actual_s = result["processing_time_ms"] / 1000
    print(f"\n[PERF] Actual inference time: {actual_s:.1f}s — document this, don't fight it")


# ── 4. CONCURRENCY (the key test) ─────────────────────────────────────────
@pytest.mark.integration
def test_concurrent_submissions_dont_block_each_other():
    """
    Fires N submissions simultaneously and checks they were all accepted
    quickly. If run_in_executor is working correctly, submission time for
    N concurrent requests should still be near SUBMISSION_SLA_MS each.

    If this test shows submission times scaling linearly with N, inference
    is blocking the event loop — the ThreadPoolExecutor isn't being used
    correctly, or something before run_in_executor is synchronous.
    """
    N = 4
    texts = [f"concurrent concept number {i}" for i in range(N)]
    submission_times_ms = []
    task_ids = []

    def submit(text: str) -> tuple[str, float]:
        start = time.perf_counter()
        res = client.post("/explain", json={"text": text})
        elapsed = (time.perf_counter() - start) * 1000
        assert res.status_code == 202
        return res.json()["task_id"], elapsed

    with concurrent.futures.ThreadPoolExecutor(max_workers=N) as pool:
        results = list(pool.map(submit, texts))

    for task_id, elapsed_ms in results:
        task_ids.append(task_id)
        submission_times_ms.append(elapsed_ms)
        assert elapsed_ms < SUBMISSION_SLA_MS * 2, (  # 2x headroom for concurrent load
            f"Submission {task_id} took {elapsed_ms:.1f}ms under concurrent load — "
            f"suggests the event loop is being blocked before asyncio.create_task()."
        )

    print(f"\n[PERF] Concurrent submission times: {[f'{t:.0f}ms' for t in submission_times_ms]}")
    print(f"[PERF] Max: {max(submission_times_ms):.0f}ms  Mean: {sum(submission_times_ms)/len(submission_times_ms):.0f}ms")


# ── 5. PROFILING HELPER TEST ──────────────────────────────────────────────
@pytest.mark.integration
def test_health_documents_real_sla():
    """
    Confirms your /health endpoint is honest about inference time,
    which matters for grant demos and investor due diligence — you don't
    want reviewers hitting the API and thinking 30s response = broken.
    """
    res = client.get("/health")
    assert res.status_code == 200
    body = res.json()
    assert "inference_sla_note" in body, (
        "Add an 'inference_sla_note' field to /health explaining that "
        "LLM inference takes seconds and clients should poll. This prevents "
        "engineers evaluating your API from thinking a 30s response is a bug."
    )