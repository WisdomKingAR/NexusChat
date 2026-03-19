import requests
import uuid

BASE_URL = "http://localhost:8001"
TIMEOUT = 30

def get_admin_token():
    email = "admin@test.com"
    password = "TestPass123!"
    display_name = "System Admin"
    headers = {"Content-Type": "application/json"}
    try:
        resp = requests.post(f"{BASE_URL}/api/auth/login", json={"email": email, "password": password}, headers=headers, timeout=TIMEOUT)
        if resp.status_code == 201: return resp.json()["access_token"]
    except: pass
    try:
        resp = requests.post(f"{BASE_URL}/api/auth/register", json={"email": email, "password": password, "display_name": display_name}, headers=headers, timeout=TIMEOUT)
        if resp.status_code == 201: return resp.json()["access_token"]
        elif resp.status_code == 400:
            resp = requests.post(f"{BASE_URL}/api/auth/login", json={"email": email, "password": password}, headers=headers, timeout=TIMEOUT)
            if resp.status_code == 201: return resp.json()["access_token"]
    except: pass
    raise RuntimeError("Failed to obtain admin token")

def test_post_api_rooms_room_messages_send_message():
    admin_token = get_admin_token()
    headers = {"Authorization": f"Bearer {admin_token}", "Content-Type": "application/json"}
    room_id = None
    message_id = None
    try:
        # Create room
        res_create = requests.post(f"{BASE_URL}/api/rooms", json={"name": f"Room-{uuid.uuid4().hex[:4]}"}, headers=headers, timeout=TIMEOUT)
        assert res_create.status_code == 201, f"Room creation failed: {res_create.status_code}"
        room_id = res_create.json()["id"]

        # Send message
        res_send = requests.post(f"{BASE_URL}/api/rooms/{room_id}/messages", json={"content": "Test message"}, headers=headers, timeout=TIMEOUT)
        assert res_send.status_code == 201, f"Send message failed: {res_send.status_code}"
        message_id = res_send.json()["id"]
        assert message_id, "Message ID missing"

    finally:
        if room_id:
            try: requests.delete(f"{BASE_URL}/api/rooms/{room_id}", headers=headers, timeout=TIMEOUT)
            except: pass

if __name__ == "__main__":
    test_post_api_rooms_room_messages_send_message()
