import requests
import pytest

BASE_URL = "http://127.0.0.1:10000"

def test_stress_inputs_do_not_crash():
    stress_inputs = [
        "A",                    # Single character
        "!" * 2000,             # Extremely long input
        "🚀🔥💎",               # Emojis
        "{\"json\": \"bad\"}",  # JSON-like structure
    ]
    for text in stress_inputs:
        response = requests.post(f"{BASE_URL}/explain", json={"text": text})
        # We ensure the API handles these gracefully, not a 500 error
        # API returns 202 (accepted) for valid requests, 422 for validation errors
        assert response.status_code in [202, 422], f"Unexpected status {response.status_code} for input: {text[:50]}"
