import requests

BASE_URL = "http://localhost:8001"
TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbkB0ZXN0LmNvbSIsImV4cCI6MTc3Mzk4NjE3M30.0yfeSYzVT0s1KKpSldMA9bbAHT8tQWU1Ew2VvUAnGgk"
HEADERS = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json",
}

def test_list_messages():
    try:
        # Step 1: List rooms to get a valid room_id for messages listing
        rooms_resp = requests.get(f"{BASE_URL}/api/rooms", headers=HEADERS, timeout=30)
        assert rooms_resp.status_code == 200, f"Failed to list rooms, status {rooms_resp.status_code}"

        rooms_data = rooms_resp.json()
        assert isinstance(rooms_data, list), "Rooms response is not a list"

        if not rooms_data:
            # Create a room as no rooms exist
            room_payload = {"name": "test-room-for-messages"}
            create_resp = requests.post(f"{BASE_URL}/api/rooms", headers=HEADERS, json=room_payload, timeout=30)
            assert create_resp.status_code == 201, f"Failed to create room, status {create_resp.status_code}"
            room = create_resp.json()
            room_id = room.get("id")
            assert room_id is not None, "Created room ID is missing"
            created_room = True
        else:
            room_id = rooms_data[0].get("id")
            assert room_id is not None, "Room ID is missing in list"
            created_room = False

        # Step 2: Fetch messages for the room
        messages_resp = requests.get(f"{BASE_URL}/api/rooms/{room_id}/messages", headers=HEADERS, timeout=30)
        assert messages_resp.status_code == 200, f"Failed to fetch messages, status {messages_resp.status_code}"

        messages_data = messages_resp.json()
        assert isinstance(messages_data, list), "Messages response is not a list"

    finally:
        # Cleanup - delete created room if created
        if 'created_room' in locals() and created_room:
            try:
                del_resp = requests.delete(f"{BASE_URL}/api/rooms/{room_id}", headers=HEADERS, timeout=30)
                assert del_resp.status_code == 200, f"Failed to delete room in cleanup, status {del_resp.status_code}"
            except Exception:
                pass

test_list_messages()