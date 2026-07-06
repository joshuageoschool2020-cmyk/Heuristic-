import requests
import time
import pytest

BASE_URL = "http://127.0.0.1:10000"

def test_output_remains_analytical():
    # Test cases that often trigger "conversational" AI filler
    test_inputs = ["Explain gravity", "Summarize this topic", "Analyze market trends"]
    
    # Words we do NOT want to see (conversational fillers)
    forbidden_words = ["sure", "happy to help", "i think", "as an ai", "certainly"]
    
    for text in test_inputs:
        # Submit task and get task_id
        response = requests.post(f"{BASE_URL}/explain", json={"text": text})
        assert response.status_code == 202, f"Expected 202, got {response.status_code}"
        task_id = response.json()["task_id"]
        
        # Poll until complete
        for _ in range(60):
            status_response = requests.get(f"{BASE_URL}/tasks/{task_id}")
            data = status_response.json()
            if data.get("status") == "complete":
                break
            time.sleep(1)
        
        # Now check the result
        assert data.get("status") == "complete", f"Task did not complete: {data}"
        analysis = data["result"].lower()
        
        # Ensure the AI didn't use conversational filler
        for word in forbidden_words:
            assert word not in analysis, f"Found conversational filler '{word}' in response: {analysis}"
