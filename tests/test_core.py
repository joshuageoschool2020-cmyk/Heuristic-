import requests
import time
import pytest

BASE_URL = "http://127.0.0.1:10000"

def test_health_endpoint():
    # Verify the root endpoint is alive
    response = requests.get(f"{BASE_URL}/")
    assert response.status_code == 200

def test_basic_request_returns_valid_schema():
    # 1. Define payload and submit the task
    payload = {"text": "explain the heuristic core"}
    response = requests.post(f"{BASE_URL}/explain", json=payload)
    assert response.status_code == 202
    
    task_id = response.json()["task_id"]

    # 2. Poll the status endpoint until it's 'completed'
    data = {}
    for _ in range(60):
        status_response = requests.get(f"{BASE_URL}/tasks/{task_id}")
        data = status_response.json()
        if data.get("status") == "complete":
            break
        time.sleep(1)
    
    # 3. Now assert the final result exists
    assert data.get("status") == "complete" 
    assert "result" in data
    assert "confidence" in data
    assert isinstance(data["result"], str)