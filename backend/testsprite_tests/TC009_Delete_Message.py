import requests

BASE_URL = "http://localhost:8001"
TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbkB0ZXN0LmNvbSIsImV4cCI6MTc3Mzk4NjE3M30.0yfeSYzVT0s1KKpSldMA9bbAHT8tQWU1Ew2VvUAnGgk"
HEADERS = {"Authorization": f"Bearer {TOKEN}"}
TIMEOUT = 30

def test_TC009_delete_message():
    # To delete a message, we first need a message. We'll create a room, then send a message, then delete the message.
    room_id = None
    message_id = None
    try:
        # Create a room (admin only)
        room_payload = {"name": "test_room_for_message_deletion"}
        room_resp = requests.post(f"{BASE_URL}/api/rooms", json=room_payload, headers=HEADERS, timeout=TIMEOUT)
        assert room_resp.status_code == 201, f"Room creation failed: {room_resp.text}"
        room_id = room_resp.json().get("id")
        assert room_id is not None, "Room ID not returned."

        # Get current user profile to get sender_id for message
        profile_resp = requests.get(f"{BASE_URL}/api/auth/me", headers=HEADERS, timeout=TIMEOUT)
        assert profile_resp.status_code == 200, f"Get profile failed: {profile_resp.text}"
        sender_id = profile_resp.json().get("id")
        assert sender_id is not None, "Sender ID not found in profile."

        # Insert a message into the room
        message_payload = {"content": "Test message to be deleted."}
        message_resp = requests.post(f"{BASE_URL}/api/rooms/{room_id}/messages", json=message_payload, headers=HEADERS, timeout=TIMEOUT)
        assert message_resp.status_code == 201, f"Message creation failed: {message_resp.text}"
        message_id = message_resp.json().get("id")
        assert message_id is not None, "Message ID not returned."

        # Delete the message as admin
        delete_resp = requests.delete(f"{BASE_URL}/api/messages/{message_id}", headers=HEADERS, timeout=TIMEOUT)
        assert delete_resp.status_code == 200, f"Message deletion failed: {delete_resp.text}"

    finally:
        # Cleanup: delete message if exists and was not deleted
        if message_id:
            try:
                requests.delete(f"{BASE_URL}/api/messages/{message_id}", headers=HEADERS, timeout=TIMEOUT)
            except Exception:
                pass
        # Delete the room created
        if room_id:
            try:
                requests.delete(f"{BASE_URL}/api/rooms/{room_id}", headers=HEADERS, timeout=TIMEOUT)
            except Exception:
                pass

test_TC009_delete_message()
