import requests
import pytest

BASE_URL = "http://127.0.0.1:10000"

def test_output_remains_analytical():
    # Test cases that often trigger "conversational" AI filler
    test_inputs = ["Explain gravity", "Summarize this topic", "Analyze market trends"]
    
    # Words we do NOT want to see (conversational fillers)
    forbidden_words = ["sure", "happy to help", "i think", "as an ai", "certainly"]
    
    for text in test_inputs:
        response = requests.post(f"{BASE_URL}/explain", json={"text": text})
        data = response.json()
        analysis = data["result"].lower()
        
        # Ensure the AI didn't use conversational filler
        for word in forbidden_words:
            assert word not in analysis, f"Found conversational filler '{word}' in response: {analysis}"