import requests
import uuid

BASE_URL = "http://localhost:8001"
TIMEOUT = 30

def get_admin_token():
    email = "admin@test.com"
    password = "TestPass123!"
    display_name = "System Admin"
    headers = {"Content-Type": "application/json"}
    
    # 1. Try Login
    try:
        resp = requests.post(f"{BASE_URL}/api/auth/login", json={"email": email, "password": password}, headers=headers, timeout=TIMEOUT)
        if resp.status_code == 201: return resp.json()["access_token"]
    except: pass
    
    # 2. Try Register
    try:
        resp = requests.post(f"{BASE_URL}/api/auth/register", json={"email": email, "password": password, "display_name": display_name}, headers=headers, timeout=TIMEOUT)
        if resp.status_code == 201: return resp.json()["access_token"]
        elif resp.status_code == 400:
             resp = requests.post(f"{BASE_URL}/api/auth/login", json={"email": email, "password": password}, headers=headers, timeout=TIMEOUT)
             if resp.status_code == 201: return resp.json()["access_token"]
    except: pass
    raise RuntimeError("Failed to obtain admin token")

def get_participant_token():
    email = f"user_{uuid.uuid4().hex[:8]}@test.com"
    password = "UserPass123!"
    headers = {"Content-Type": "application/json"}
    resp = requests.post(f"{BASE_URL}/api/auth/register", json={"email": email, "password": password, "display_name": "Regular User"}, headers=headers, timeout=TIMEOUT)
    if resp.status_code == 201: return resp.json()["access_token"]
    return None

def test_post_api_rooms_create_new_room_admin_only():
    admin_token = get_admin_token()
    part_token = get_participant_token()
    
    # 1. Admin creates room - expect 201
    room_name = f"Admin Room {uuid.uuid4().hex[:8]}"
    resp = requests.post(f"{BASE_URL}/api/rooms", json={"name": room_name}, headers={"Authorization": f"Bearer {admin_token}"}, timeout=TIMEOUT)
    assert resp.status_code == 201, f"Admin failed to create room: {resp.status_code}"
    room_id = resp.json()["id"]

    # 2. Participant attempt - expect 403
    resp_p = requests.post(f"{BASE_URL}/api/rooms", json={"name": "Fail Room"}, headers={"Authorization": f"Bearer {part_token}"}, timeout=TIMEOUT)
    assert resp_p.status_code == 403, f"Participant should have been forbidden, got {resp_p.status_code}"

    # 3. Empty name - expect 422 (FastAPI validation)
    resp_e = requests.post(f"{BASE_URL}/api/rooms", json={"name": ""}, headers={"Authorization": f"Bearer {admin_token}"}, timeout=TIMEOUT)
    assert resp_e.status_code == 422, f"Expected 422 for empty name, got {resp_e.status_code}"

    # Cleanup
    requests.delete(f"{BASE_URL}/api/rooms/{room_id}", headers={"Authorization": f"Bearer {admin_token}"}, timeout=TIMEOUT)

if __name__ == "__main__":
    test_post_api_rooms_create_new_room_admin_only()
