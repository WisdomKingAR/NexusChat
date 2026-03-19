import requests

BASE_URL = "http://localhost:8001"
ADMIN_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbkB0ZXN0LmNvbSIsImV4cCI6MTc3Mzk4NjE3M30.0yfeSYzVT0s1KKpSldMA9bbAHT8tQWU1Ew2VvUAnGgk"
HEADERS = {"Authorization": f"Bearer {ADMIN_TOKEN}"}
TIMEOUT = 30

def test_get_api_rooms_list_rooms():
    url = f"{BASE_URL}/api/rooms"
    try:
        response = requests.get(url, headers=HEADERS, timeout=TIMEOUT)
        # Assert HTTP status code 200 OK
        assert response.status_code == 200, f"Expected 200 OK but got {response.status_code}"
        # Assert response body is a list (of rooms)
        rooms = response.json()
        assert isinstance(rooms, list), f"Expected response to be list but got {type(rooms)}"
        # Optionally: If list not empty, rooms have expected keys
        if rooms:
            for room in rooms:
                assert isinstance(room, dict), "Each room should be a dictionary"
                assert "id" in room or "room_id" in room or "name" in room, "Room object missing expected keys"
    except requests.RequestException as e:
        assert False, f"Request failed: {e}"

test_get_api_rooms_list_rooms()
