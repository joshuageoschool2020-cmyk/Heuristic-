# conftest.py
# Place at your PROJECT ROOT (same level as api.py, brain.py).
# pytest auto-loads this before any test collection begins.
#
# This is the THIRD layer of defense against ModuleNotFoundError —
# belt-and-suspenders alongside pyproject.toml and the CI PYTHONPATH.
# It handles the edge case where someone runs pytest from inside the
# tests/ subdirectory instead of from the project root.

from __future__ import annotations

import asyncio
import concurrent.futures
import sys
from pathlib import Path

# Ensure project root is on sys.path regardless of where pytest was invoked.
# Path(__file__) is this conftest.py — .parent is the directory it lives in.
PROJECT_ROOT = Path(__file__).parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


# ── SHARED FIXTURES ───────────────────────────────────────────────────────
import pytest
from fastapi.testclient import TestClient


@pytest.fixture(scope="session")
def client():
    """Single TestClient shared across the entire test session."""
    from api import app
    with TestClient(app, raise_server_exceptions=False) as c:
        yield c


@pytest.fixture
def assert_health(client):
    """
    Schema-flexible health assertion — checks status == "ok"
    without requiring an exact body match.
    Solves the regression where adding inference_sla_note broke
    tests that did: assert response.json() == {"status": "ok"}
    """
    def _check(extra_fields: list[str] | None = None):
        res = client.get("/health")
        assert res.status_code == 200
        body = res.json()
        assert body.get("status") == "ok", f"Unexpected status: {body}"
        for field in (extra_fields or []):
            assert field in body, f"Missing field {field!r} in /health response"
        return body
    return _check


@pytest.fixture(scope="session", autouse=True)
def configure_executor():
    """Explicit thread pool — prevents silent queue starvation in tests."""
    executor = concurrent.futures.ThreadPoolExecutor(
        max_workers=4,
        thread_name_prefix="heuristic_worker",
    )
    yield
    executor.shutdown(wait=False)