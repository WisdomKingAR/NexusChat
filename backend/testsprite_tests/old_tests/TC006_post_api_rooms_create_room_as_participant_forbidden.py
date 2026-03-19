import requests

BASE_URL = "http://localhost:8001"
PARTICIPANT_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbkB0ZXN0LmNvbSIsImV4cCI6MTc3Mzk4NjE3M30.0yfeSYzVT0s1KKpSldMA9bbAHT8tQWU1Ew2VvUAnGgk"
TIMEOUT = 30

def test_post_api_rooms_create_room_as_participant_forbidden():
    url = f"{BASE_URL}/api/rooms"
    headers = {
        "Authorization": f"Bearer {PARTICIPANT_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {
        "name": "Test Room Forbidden"
    }
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=TIMEOUT)
    except requests.RequestException as e:
        assert False, f"Request failed: {e}"

    assert response.status_code == 403, f"Expected 403 Forbidden but got {response.status_code}"
    json_resp = {}
    try:
        json_resp = response.json()
    except ValueError:
        assert False, "Response is not valid JSON"

    # The error message should be "You don't have permission to do this."
    expected_message = "You don't have permission to do this."
    # Sometimes the error message could be in a field such as 'detail' or 'error'
    error_message = json_resp.get("detail") or json_resp.get("error") or ""
    assert expected_message in error_message, f"Expected error message to contain '{expected_message}' but got '{error_message}'"


test_post_api_rooms_create_room_as_participant_forbidden()