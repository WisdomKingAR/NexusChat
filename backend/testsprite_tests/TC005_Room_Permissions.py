import requests
import json

BASE_URL = "http://localhost:8001"
ADMIN_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbkB0ZXN0LmNvbSIsImV4cCI6MTc3Mzk4NjE3M30.0yfeSYzVT0s1KKpSldMA9bbAHT8tQWU1Ew2VvUAnGgk"
PARTICIPANT_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJwYXJ0aWNpcGFudEB0ZXN0LmNvbSIsImV4cCI6MTc3Mzk4NjE3M30.TKh6Nmf998XhqpsTYfnVURh8UPvTH8VYIQh_9V3MN4I"

HEADERS_ADMIN = {
    "Authorization": f"Bearer {ADMIN_TOKEN}",
    "Content-Type": "application/json"
}

HEADERS_PARTICIPANT = {
    "Authorization": f"Bearer {PARTICIPANT_TOKEN}",
    "Content-Type": "application/json"
}

TIMEOUT = 30


def test_TC005_room_permissions():
    room_id = None
    try:
        # 1. Admin creates a room with valid name - expect 201 Created
        room_data = {"name": "test-room-permissions"}
        resp = requests.post(f"{BASE_URL}/api/rooms", headers=HEADERS_ADMIN, json=room_data, timeout=TIMEOUT)
        assert resp.status_code == 201, f"Admin room creation failed: {resp.status_code} {resp.text}"
        body = resp.json()
        assert "id" in body, "Response missing 'id' for created room"
        room_id = body["id"]

        # 2. Participant tries to create a room - expect 403 Forbidden
        participant_room_data = {"name": "participant-room"}
        resp = requests.post(f"{BASE_URL}/api/rooms", headers=HEADERS_PARTICIPANT, json=participant_room_data, timeout=TIMEOUT)
        assert resp.status_code == 403, f"Participant room creation not forbidden: {resp.status_code} {resp.text}"

        # 3. Admin tries to create a room with empty name - expect 400 Bad Request with validation error
        empty_name_data = {"name": ""}
        resp = requests.post(f"{BASE_URL}/api/rooms", headers=HEADERS_ADMIN, json=empty_name_data, timeout=TIMEOUT)
        assert resp.status_code == 400, f"Empty name room creation should fail 400: {resp.status_code} {resp.text}"
        error_response = resp.json()
        # Check for validation error 'name required' in response
        error_text = json.dumps(error_response).lower()
        assert "name required" in error_text, f"Expected validation error 'name required', got: {error_response}"

        # 4. Participant tries to delete the admin room - expect 403 Forbidden
        resp = requests.delete(f"{BASE_URL}/api/rooms/{room_id}", headers=HEADERS_PARTICIPANT, timeout=TIMEOUT)
        assert resp.status_code == 403, f"Participant deleting room not forbidden: {resp.status_code} {resp.text}"

    finally:
        # Cleanup: Admin deletes the room if created
        if room_id:
            try:
                resp = requests.delete(f"{BASE_URL}/api/rooms/{room_id}", headers=HEADERS_ADMIN, timeout=TIMEOUT)
                # Allow 200 OK or 404 Not Found if already deleted
                assert resp.status_code in (200, 404), f"Failed to cleanup room: {resp.status_code} {resp.text}"
            except Exception:
                pass


test_TC005_room_permissions()
