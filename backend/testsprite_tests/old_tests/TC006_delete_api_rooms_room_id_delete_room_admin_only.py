import requests

BASE_URL = "http://localhost:8001"
ADMIN_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbkB0ZXN0LmNvbSIsImV4cCI6MTc3Mzk4NjE3M30.0yfeSYzVT0s1KKpSldMA9bbAHT8tQWU1Ew2VvUAnGgk"
PARTICIPANT_TOKEN = None  # Will be set after participant login

HEADERS_ADMIN = {
    "Authorization": f"Bearer {ADMIN_TOKEN}",
    "Content-Type": "application/json"
}

TIMEOUT = 30


def get_participant_token():
    """Helper to get a participant token by registering and logging in a participant user."""
    try:
        # Register participant user
        email = "participant_test_user@example.com"
        password = "TestPass1234!"  # Stronger password to avoid validation errors
        reg_resp = requests.post(
            f"{BASE_URL}/api/auth/register",
            json={"email": email, "password": password},
            headers={"Content-Type": "application/json"},
            timeout=TIMEOUT,
        )
        if reg_resp.status_code not in (201, 409):
            reg_resp.raise_for_status()

        # Login participant user
        login_resp = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": email, "password": password},
            timeout=TIMEOUT,
        )
        login_resp.raise_for_status()
        token = login_resp.json().get("token")  # Adjusted key per PRD indication
        assert token is not None, "No token received on participant login"
        return token
    except Exception as e:
        raise RuntimeError(f"Failed to obtain participant token: {e}")


def test_delete_room_admin_and_participant():
    global PARTICIPANT_TOKEN
    PARTICIPANT_TOKEN = get_participant_token()
    headers_participant = {
        "Authorization": f"Bearer {PARTICIPANT_TOKEN}",
        "Content-Type": "application/json"
    }

    # Step 1: Create a new room using admin token
    room_name = "test_room_to_delete"
    create_resp = requests.post(
        f"{BASE_URL}/api/rooms",
        headers=HEADERS_ADMIN,
        json={"name": room_name},
        timeout=TIMEOUT,
    )
    assert create_resp.status_code == 201, f"Room creation failed: {create_resp.text}"
    room_id = create_resp.json().get("id")
    assert room_id is not None, "Room ID not returned in creation response"

    try:
        # Step 2: Verify room exists in rooms list for admin and participant
        for token, role in [(ADMIN_TOKEN, "admin"), (PARTICIPANT_TOKEN, "participant")]:
            resp = requests.get(
                f"{BASE_URL}/api/rooms",
                headers={"Authorization": f"Bearer {token}"},
                timeout=TIMEOUT,
            )
            assert resp.status_code == 200, f"Rooms list fetch failed for {role}: {resp.text}"
            rooms = resp.json()
            assert any(room.get("id") == room_id for room in rooms), f"Room not in {role} rooms list"

        # Step 3: Delete the room using admin token, expect 200 OK
        delete_resp = requests.delete(
            f"{BASE_URL}/api/rooms/{room_id}",
            headers=HEADERS_ADMIN,
            timeout=TIMEOUT,
        )
        assert delete_resp.status_code == 200, f"Admin delete failed: {delete_resp.text}"

        # Step 4: Verify room is removed from rooms list for admin and participant
        for token, role in [(ADMIN_TOKEN, "admin"), (PARTICIPANT_TOKEN, "participant")]:
            resp = requests.get(
                f"{BASE_URL}/api/rooms",
                headers={"Authorization": f"Bearer {token}"},
                timeout=TIMEOUT,
            )
            assert resp.status_code == 200, f"Rooms list fetch failed for {role} after delete: {resp.text}"
            rooms = resp.json()
            assert all(room.get("id") != room_id for room in rooms), f"Deleted room still present for {role}"

        # Step 5: Verify cascade delete of messages by getting messages for deleted room - expect 404 or empty?
        messages_resp = requests.get(
            f"{BASE_URL}/api/rooms/{room_id}/messages",
            headers=HEADERS_ADMIN,
            timeout=TIMEOUT,
        )
        # According to cascade delete, messages should be gone, room doesn't exist, expect 404 or empty array
        assert messages_resp.status_code in (200, 404), f"Unexpected messages fetch status code: {messages_resp.status_code}"
        if messages_resp.status_code == 200:
            messages = messages_resp.json()
            assert messages == [] or messages is None, "Messages still exist for deleted room"

        # Step 6: Attempt to delete a room with participant token, expect 403 Forbidden
        # Create another room to test this
        create_resp_part = requests.post(
            f"{BASE_URL}/api/rooms",
            headers=HEADERS_ADMIN,
            json={"name": "test_room_for_participant_delete"},
            timeout=TIMEOUT,
        )
        assert create_resp_part.status_code == 201, f"Second room creation failed: {create_resp_part.text}"
        room_id_part = create_resp_part.json().get("id")
        assert room_id_part is not None, "Second room ID not returned"

        # Try delete with participant token
        delete_resp_part = requests.delete(
            f"{BASE_URL}/api/rooms/{room_id_part}",
            headers=headers_participant,
            timeout=TIMEOUT,
        )
        assert delete_resp_part.status_code == 403, f"Participant should not delete room: {delete_resp_part.status_code} {delete_resp_part.text}"

        # Cleanup the second room with admin token
        del_resp_cleanup = requests.delete(
            f"{BASE_URL}/api/rooms/{room_id_part}",
            headers=HEADERS_ADMIN,
            timeout=TIMEOUT,
        )
        assert del_resp_cleanup.status_code == 200, f"Cleanup delete failed: {del_resp_cleanup.text}"

    finally:
        # Cleanup: Ensure the initially created room is deleted if still exists
        rooms_resp = requests.get(
            f"{BASE_URL}/api/rooms",
            headers=HEADERS_ADMIN,
            timeout=TIMEOUT,
        )
        if rooms_resp.status_code == 200:
            rooms = rooms_resp.json()
            if any(room.get("id") == room_id for room in rooms):
                requests.delete(
                    f"{BASE_URL}/api/rooms/{room_id}",
                    headers=HEADERS_ADMIN,
                    timeout=TIMEOUT,
                )


test_delete_room_admin_and_participant()
