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

def test_put_api_users_user_role_update_by_admin():
    admin_token = get_admin_token()
    headers = {"Authorization": f"Bearer {admin_token}", "Content-Type": "application/json"}
    user_id = None
    try:
        # Create a user to update
        new_email = f"user_{uuid.uuid4().hex[:8]}@test.com"
        resp_reg = requests.post(f"{BASE_URL}/api/auth/register", json={"email": new_email, "password": "StrongPassword!123", "display_name": "Test"}, timeout=TIMEOUT)
        user_id = resp_reg.json()["user"]["id"]

        # Update role to moderator
        resp_upd = requests.put(f"{BASE_URL}/api/users/{user_id}/role", headers=headers, json={"role": "moderator"}, timeout=TIMEOUT)
        assert resp_upd.status_code == 200, f"Role update failed: {resp_upd.status_code}"
        assert resp_upd.json()["status"] == "success"

    finally:
        if user_id:
            try: requests.delete(f"{BASE_URL}/api/users/{user_id}", headers=headers, timeout=TIMEOUT)
            except: pass

if __name__ == "__main__":
    test_put_api_users_user_role_update_by_admin()