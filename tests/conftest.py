import pytest
import requests
import time

@pytest.fixture(scope="session", autouse=True)
def wait_for_server():
    # Change this URL if your app's health endpoint is different
    url = "http://127.0.0.1:10000/" 
    timeout = 30
    start_time = time.time()
    
    while time.time() - start_time < timeout:
        try:
            if requests.get(url).status_code == 200:
                return True
        except requests.exceptions.ConnectionError:
            pass
        time.sleep(1)
    
    raise RuntimeError(f"Server not ready after {timeout} seconds")