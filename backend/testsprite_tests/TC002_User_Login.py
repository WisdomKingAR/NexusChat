import requests
from requests.exceptions import RequestException

BASE_URL = "http://localhost:8001"
LOGIN_ENDPOINT = "/api/auth/login"
TIMEOUT = 30
TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbkB0ZXN0LmNvbSIsImV4cCI6MTc3Mzk4NjE3M30.0yfeSYzVT0s1KKpSldMA9bbAHT8tQWU1Ew2VvUAnGgk"

def test_user_login():
    url = BASE_URL + LOGIN_ENDPOINT
    login_payload = {
        "email": "admin@test.com",
        "password": "dummyPassword123!"
    }

    try:
        response = requests.post(url, json=login_payload, timeout=TIMEOUT)
    except RequestException as e:
        assert False, f"Login request failed: {e}"

    # Correct expected status code per PRD is 200 OK
    assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"

    try:
        json_data = response.json()
    except Exception:
        assert False, "Response is not valid JSON."

    assert "token" in json_data, "Response JSON does not contain 'token' field."
    assert isinstance(json_data["token"], str) and len(json_data["token"]) > 0, "'token' field is empty or not a string."


test_user_login()
