import requests

BASE_URL = "http://localhost:8001"
TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbkB0ZXN0LmNvbSIsImV4cCI6MTc3Mzk4NjE3M30.0yfeSYzVT0s1KKpSldMA9bbAHT8tQWU1Ew2VvUAnGgk"
HEADERS = {"Authorization": f"Bearer {TOKEN}", "Content-Type": "application/json"}
TIMEOUT = 30

def test_delete_room():
    room_id = None
    try:
        # Create a new room first
        create_resp = requests.post(
            f"{BASE_URL}/api/rooms",
            headers=HEADERS,
            json={"name": "test_delete_room"},
            timeout=TIMEOUT,
        )
        assert create_resp.status_code == 201, f"Room creation failed: {create_resp.text}"
        data = create_resp.json()
        room_id = data.get("id")
        assert room_id, "Created room ID not found."

        # Delete the created room
        delete_resp = requests.delete(
            f"{BASE_URL}/api/rooms/{room_id}",
            headers=HEADERS,
            timeout=TIMEOUT,
        )
        assert delete_resp.status_code == 200, f"Room deletion failed: {delete_resp.text}"

        # Verify room no longer exists by listing rooms
        list_resp = requests.get(
            f"{BASE_URL}/api/rooms",
            headers=HEADERS,
            timeout=TIMEOUT,
        )
        assert list_resp.status_code == 200, f"Room listing failed: {list_resp.text}"
        rooms = list_resp.json()
        assert all(room.get("id") != room_id for room in rooms), "Deleted room still present in list."

    finally:
        # Cleanup: If the room still exists, delete it to avoid leftovers
        if room_id:
            try:
                requests.delete(
                    f"{BASE_URL}/api/rooms/{room_id}",
                    headers=HEADERS,
                    timeout=TIMEOUT,
                )
            except Exception:
                pass

test_delete_room()
