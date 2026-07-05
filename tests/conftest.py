import os
import time
import requests
import pytest

@pytest.fixture(scope="session", autouse=True)
def wait_for_server():
    url = os.getenv("TEST_SERVER_URL", "http://127.0.0.1:10000/")
    timeout = int(os.getenv("TEST_SERVER_TIMEOUT", "120"))
    start_time = time.time()

    while time.time() - start_time < timeout:
        try:
            resp = requests.get(url, timeout=2)
            if resp.status_code == 200:
                return True
            print(f"Health check returned {resp.status_code} for {url}")
        except requests.exceptions.RequestException as exc:
            print(f"Health check failed ({exc}) for {url}")
        time.sleep(1)

    raise RuntimeError(f"Server not ready after {timeout} seconds (checked {url})")