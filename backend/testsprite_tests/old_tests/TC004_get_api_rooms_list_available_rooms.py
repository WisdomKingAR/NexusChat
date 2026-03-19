import requests

def test_get_api_rooms_list_available_rooms():
    base_url = "http://localhost:8001"
    endpoint = "/api/rooms"
    token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbkB0ZXN0LmNvbSIsImV4cCI6MTc3Mzk4NjE3M30.0yfeSYzVT0s1KKpSldMA9bbAHT8tQWU1Ew2VvUAnGgk"
    headers = {
        "Authorization": f"Bearer {token}"
    }
    try:
        response = requests.get(f"{base_url}{endpoint}", headers=headers, timeout=30)
        response.raise_for_status()
        assert response.status_code == 200
        rooms = response.json()
        assert isinstance(rooms, list)
        # Check if rooms are ordered by some key, e.g. 'name' if present
        if len(rooms) > 1:
            keys = [room.get('name', '') for room in rooms if 'name' in room]
            # Verify the list is sorted ascending by name
            assert keys == sorted(keys)
    except requests.exceptions.RequestException as e:
        assert False, f"Request failed: {e}"

test_get_api_rooms_list_available_rooms()