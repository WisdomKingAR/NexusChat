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

def test_delete_api_messages_message_by_admin():
    admin_token = get_admin_token()
    headers = {"Authorization": f"Bearer {admin_token}", "Content-Type": "application/json"}
    room_id = None
    message_id = None
    try:
        # Create room
        res_room = requests.post(f"{BASE_URL}/api/rooms", json={"name": "Delete-Test-Room"}, headers=headers, timeout=TIMEOUT)
        room_id = res_room.json()["id"]

        # Create message
        res_msg = requests.post(f"{BASE_URL}/api/rooms/{room_id}/messages", json={"content": "ToDelete"}, headers=headers, timeout=TIMEOUT)
        message_id = res_msg.json()["id"]

        # Delete message
        res_del = requests.delete(f"{BASE_URL}/api/messages/{message_id}", headers=headers, timeout=TIMEOUT)
        assert res_del.status_code == 200, f"Delete failed: {res_del.status_code}"

    finally:
        if room_id:
            try: requests.delete(f"{BASE_URL}/api/rooms/{room_id}", headers=headers, timeout=TIMEOUT)
            except: pass

if __name__ == "__main__":
    test_delete_api_messages_message_by_admin()