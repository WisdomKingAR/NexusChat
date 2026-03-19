import requests

BASE_URL = "http://localhost:8001"
TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbkB0ZXN0LmNvbSIsImV4cCI6MTc3Mzk4NjE3M30.0yfeSYzVT0s1KKpSldMA9bbAHT8tQWU1Ew2VvUAnGgk"
HEADERS = {
    "Authorization": f"Bearer {TOKEN}",
    "Accept": "application/json"
}
TIMEOUT = 30


def test_get_api_auth_me_with_valid_token():
    url = f"{BASE_URL}/api/auth/me"
    try:
        response = requests.get(url, headers=HEADERS, timeout=TIMEOUT)
        response.raise_for_status()
    except requests.RequestException as e:
        assert False, f"Request to GET /api/auth/me failed: {e}"

    assert response.status_code == 200, f"Expected 200 OK but got {response.status_code}"
    json_data = response.json()

    # Validate that required profile fields are present and roles exist
    assert "email" in json_data, "Response JSON missing 'email'"
    assert "role" in json_data, "Response JSON missing 'role'"
    assert isinstance(json_data["email"], str) and json_data["email"], "'email' should be a non-empty string"
    assert isinstance(json_data["role"], str) and json_data["role"], "'role' should be a non-empty string"


test_get_api_auth_me_with_valid_token()