import requests

BASE_URL = "http://localhost:8001"
PROFILE_ENDPOINT = "/api/auth/me"
REGISTER_ENDPOINT = "/api/auth/register"
LOGIN_ENDPOINT = "/api/auth/login"
TIMEOUT = 30

def get_token():
    email = "test_profile@example.com"
    password = "ProfilePass123!"
    headers = {"Content-Type": "application/json"}
    
    # Register/Login
    requests.post(f"{BASE_URL}{REGISTER_ENDPOINT}", json={"email": email, "password": password, "display_name": "Profile User"}, headers=headers, timeout=TIMEOUT)
    resp = requests.post(f"{BASE_URL}{LOGIN_ENDPOINT}", json={"email": email, "password": password}, headers=headers, timeout=TIMEOUT)
    if resp.status_code == 201:
        return resp.json()["access_token"]
    return None

def test_get_api_auth_me_fetch_current_user_profile():
    token = get_token()
    assert token, "Failed to obtain token for profile test"
    
    headers = {
        "Authorization": f"Bearer {token}"
    }

    # Fetch profile - expect 200 OK
    response = requests.get(BASE_URL + PROFILE_ENDPOINT, headers=headers, timeout=TIMEOUT)
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    data = response.json()
    assert "email" in data, "Response JSON does not contain 'email'"
    assert data["email"] == "test_profile@example.com"

if __name__ == "__main__":
    test_get_api_auth_me_fetch_current_user_profile()