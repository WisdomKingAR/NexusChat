import requests
import uuid

BASE_URL = "http://localhost:8001"
TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbkB0ZXN0LmNvbSIsImV4cCI6MTc3Mzk4NjE3M30.0yfeSYzVT0s1KKpSldMA9bbAHT8tQWU1Ew2VvUAnGgk"
HEADERS = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json"
}
TIMEOUT = 30

def test_create_room():
    room_id = None
    unique_room_name = f"test-room-{uuid.uuid4()}"
    try:
        # Create a new room
        payload = {"name": unique_room_name}
        response = requests.post(f"{BASE_URL}/api/rooms", json=payload, headers=HEADERS, timeout=TIMEOUT)
        assert response.status_code == 201, f"Expected 201 Created, got {response.status_code}: {response.text}"
        json_response = response.json()
        assert "id" in json_response, f"Response JSON does not contain 'id': {json_response}"
        room_id = json_response["id"]
    finally:
        if room_id:
            # Clean up - delete the created room
            try:
                del_resp = requests.delete(f"{BASE_URL}/api/rooms/{room_id}", headers=HEADERS, timeout=TIMEOUT)
                # Deletion might be 200 OK or 204 No Content depending on implementation
                assert del_resp.status_code in (200, 204), f"Failed to delete room {room_id}. Status: {del_resp.status_code}"
            except Exception as e:
                print(f"Error cleaning up room {room_id}: {e}")

test_create_room()