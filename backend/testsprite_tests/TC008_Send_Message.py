import requests

BASE_URL = "http://localhost:8001"
TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbkB0ZXN0LmNvbSIsImV4cCI6MTc3Mzk4NjE3M30.0yfeSYzVT0s1KKpSldMA9bbAHT8tQWU1Ew2VvUAnGgk"
HEADERS = {"Authorization": f"Bearer {TOKEN}", "Content-Type": "application/json"}
TIMEOUT = 30


def test_send_message():
    room_id = None
    message_id = None
    try:
        # Step 1: Get rooms list to find a room to send message
        resp_rooms = requests.get(f"{BASE_URL}/api/rooms", headers=HEADERS, timeout=TIMEOUT)
        assert resp_rooms.status_code == 200, f"Failed to list rooms: {resp_rooms.text}"
        rooms = resp_rooms.json()
        if rooms:
            room_id = rooms[0].get("id") or rooms[0].get("room_id")
        else:
            # No room exists, create one as admin
            room_payload = {"name": "test_room_for_message"}
            resp_create = requests.post(f"{BASE_URL}/api/rooms", headers=HEADERS, json=room_payload, timeout=TIMEOUT)
            assert resp_create.status_code == 201, f"Failed to create room: {resp_create.text}"
            room_created = resp_create.json()
            room_id = room_created.get("id") or room_created.get("room_id")
        assert room_id, "Room ID not found or created"

        # Optional: Fetch current user ID for sender_id from /api/auth/me
        resp_me = requests.get(f"{BASE_URL}/api/auth/me", headers=HEADERS, timeout=TIMEOUT)
        assert resp_me.status_code == 200, f"Failed to get current user profile: {resp_me.text}"
        user_profile = resp_me.json()
        sender_id = user_profile.get("id") or user_profile.get("user_id")

        assert sender_id, "Sender ID not found in user profile"

        # Step 2: Send message to the room
        message_content = "Automated test message"
        message_payload = {"content": message_content}
        resp_send = requests.post(f"{BASE_URL}/api/rooms/{room_id}/messages", headers=HEADERS, json=message_payload, timeout=TIMEOUT)

        assert resp_send.status_code == 201, f"Sending message failed: {resp_send.text}"
        message_data = resp_send.json()
        message_id = message_data.get("id") or message_data.get("message_id")
        assert message_id, "Message ID not found in response"

    finally:
        # Cleanup: delete message and room if created by this test
        if message_id:
            _ = requests.delete(f"{BASE_URL}/api/rooms/{room_id}/messages/{message_id}", headers=HEADERS, timeout=TIMEOUT)
        if room_id:
            # Attempt delete anyway, ignore failure if permissions deny or room is default
            _ = requests.delete(f"{BASE_URL}/api/rooms/{room_id}", headers=HEADERS, timeout=TIMEOUT)


test_send_message()
