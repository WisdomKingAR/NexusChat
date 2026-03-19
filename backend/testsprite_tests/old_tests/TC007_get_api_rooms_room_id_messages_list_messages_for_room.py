import requests

BASE_URL = "http://localhost:8001"
VALID_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbkB0ZXN0LmNvbSIsImV4cCI6MTc3Mzk4NjE3M30.0yfeSYzVT0s1KKpSldMA9bbAHT8tQWU1Ew2VvUAnGgk"
INVALID_TOKEN = "Bearer invalid_or_expired_token_example"

headers_valid = {
    "Authorization": f"Bearer {VALID_TOKEN}",
    "Content-Type": "application/json"
}

headers_invalid = {
    "Authorization": INVALID_TOKEN,
    "Content-Type": "application/json"
}

def test_get_room_messages_list_messages_for_room():
    timeout = 30

    # First, create a new room using admin token to have a room to test messages retrieval.
    # We must create a room because the test requires a valid room_id resource.
    # Using the provided valid token assumed to have admin rights (from PRD context).
    room_data = {"name": "test_room_for_tc007"}

    create_room_resp = requests.post(
        f"{BASE_URL}/api/rooms",
        json=room_data,
        headers=headers_valid,
        timeout=timeout,
    )
    assert create_room_resp.status_code == 201, f"Room creation failed: {create_room_resp.text}"
    room_id = create_room_resp.json().get("id")
    assert room_id, "Room ID is missing in create response"

    try:
        # Test fetching messages with valid token (expect 200 with ordered messages and sender profiles)
        messages_resp = requests.get(
            f"{BASE_URL}/api/rooms/{room_id}/messages",
            headers=headers_valid,
            timeout=timeout,
        )
        assert messages_resp.status_code == 200, f"Expected 200 OK for valid token, got {messages_resp.status_code}"
        messages = messages_resp.json()
        assert isinstance(messages, list), "Messages response should be a list"
        last_created_at = None
        for msg in messages:
            # Validate message schema fields
            assert "id" in msg, "Message missing 'id'"
            assert "content" in msg, "Message missing 'content'"
            assert "created_at" in msg, "Message missing 'created_at'"
            assert "sender_id" in msg, "Message missing 'sender_id'"
            # Validate profiles presence
            profiles = msg.get("profiles")
            assert profiles is not None, "Message missing 'profiles'"
            assert isinstance(profiles, dict), "'profiles' should be a dict"
            assert "display_name" in profiles, "Profiles missing 'display_name'"
            assert "role" in profiles, "Profiles missing 'role'"

            # Check that messages are ordered ascending by created_at
            curr_created_at = msg["created_at"]
            if last_created_at is not None:
                assert curr_created_at >= last_created_at, "Messages not ordered by created_at ascending"
            last_created_at = curr_created_at

        # Test fetching messages with invalid/expired token (expect 401 Unauthorized)
        messages_resp_invalid = requests.get(
            f"{BASE_URL}/api/rooms/{room_id}/messages",
            headers={"Authorization": "Bearer invalid_or_expired_token"},
            timeout=timeout,
        )
        assert messages_resp_invalid.status_code == 401, f"Expected 401 for invalid token, got {messages_resp_invalid.status_code}"

    finally:
        # Cleanup: delete the room after the test
        delete_resp = requests.delete(
            f"{BASE_URL}/api/rooms/{room_id}",
            headers=headers_valid,
            timeout=timeout,
        )
        assert delete_resp.status_code == 200, f"Room cleanup failed: {delete_resp.text}"

test_get_room_messages_list_messages_for_room()