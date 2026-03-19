import requests
import uuid

BASE_URL = "http://localhost:8001"
TIMEOUT = 30

def get_admin_token():
    # Attempt to login first, then register if fails
    email = "admin@test.com"
    password = "TestPass123!"
    display_name = "System Admin"
    
    login_url = f"{BASE_URL}/api/auth/login"
    register_url = f"{BASE_URL}/api/auth/register"
    
    headers = {"Content-Type": "application/json"}
    
    # 1. Try Login
    try:
        resp = requests.post(login_url, json={"email": email, "password": password}, headers=headers, timeout=TIMEOUT)
        if resp.status_code == 201:
            return resp.json()["access_token"]
    except:
        pass
        
    # 2. Try Register (will be admin if first user)
    try:
        resp = requests.post(register_url, json={"email": email, "password": password, "display_name": display_name}, headers=headers, timeout=TIMEOUT)
        if resp.status_code == 201:
            return resp.json()["access_token"]
        elif resp.status_code == 400: # Already exists but login failed? Re-try login with right password
             resp = requests.post(login_url, json={"email": email, "password": password}, headers=headers, timeout=TIMEOUT)
             if resp.status_code == 201:
                 return resp.json()["access_token"]
    except:
        pass
    
    raise RuntimeError("Failed to obtain admin token")

def test_post_api_rooms_create_room_as_admin():
    admin_token = get_admin_token()
    headers = {
        "Authorization": f"Bearer {admin_token}",
        "Content-Type": "application/json"
    }
    
    room_name = f"Test Room {uuid.uuid4().hex[:8]}"
    create_url = f"{BASE_URL}/api/rooms"
    
    room_id = None
    try:
        response = requests.post(create_url, json={"name": room_name}, headers=headers, timeout=TIMEOUT)
        assert response.status_code == 201, f"Expected 201 Created, got {response.status_code}"
        json_data = response.json()
        assert "id" in json_data, "Response JSON does not contain 'id'"
        room_id = json_data["id"]
        assert isinstance(room_id, str) and room_id.strip(), "Room ID is invalid"
    finally:
        if room_id:
            try:
                requests.delete(f"{BASE_URL}/api/rooms/{room_id}", headers=headers, timeout=TIMEOUT)
            except:
                pass

if __name__ == "__main__":
    test_post_api_rooms_create_room_as_admin()