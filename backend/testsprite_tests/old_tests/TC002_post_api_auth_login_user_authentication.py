import requests

BASE_URL = "http://localhost:8001"
LOGIN_ENDPOINT = "/api/auth/login"
REGISTER_ENDPOINT = "/api/auth/register"
TIMEOUT = 30

def test_post_api_auth_login_user_authentication():
    # Credentials specifically for admin@test.com
    email = "admin@test.com"
    password = "TestPass123!"
    display_name = "System Admin"
    
    headers = {"Content-Type": "application/json"}
    
    # Ensure user exists for login test
    requests.post(f"{BASE_URL}{REGISTER_ENDPOINT}", json={"email": email, "password": password, "display_name": display_name}, headers=headers, timeout=TIMEOUT)

    # Correct credentials for login
    correct_credentials = {
        "email": email,
        "password": password
    }

    # Wrong password for login
    wrong_credentials = {
        "email": email,
        "password": "wrongpassword"
    }

    # Test login with correct credentials to receive 201 and JWT token (as per server.py implementation)
    try:
        resp = requests.post(
            f"{BASE_URL}{LOGIN_ENDPOINT}",
            json=correct_credentials,
            headers=headers,
            timeout=TIMEOUT
        )
    except requests.RequestException as e:
        assert False, f"Login request with correct credentials failed: {e}"

    assert resp.status_code == 201, f"Expected 201 Created (as per server.py), got {resp.status_code}. Body: {resp.text}"
    json_resp = resp.json()
    assert "access_token" in json_resp, "JWT access_token not found in response"
    token_value = json_resp.get("access_token")
    assert isinstance(token_value, str) and len(token_value) > 0, "JWT token is empty or invalid"

    # Test login with wrong password to receive 401 Unauthorized
    try:
        resp_wrong = requests.post(
            f"{BASE_URL}{LOGIN_ENDPOINT}",
            json=wrong_credentials,
            headers=headers,
            timeout=TIMEOUT
        )
    except requests.RequestException as e:
        assert False, f"Login request with wrong password failed: {e}"

    assert resp_wrong.status_code == 401, f"Expected 401 Unauthorized, got {resp_wrong.status_code}"

if __name__ == "__main__":
    test_post_api_auth_login_user_authentication()