import requests

BASE_URL = "http://localhost:8001"
TIMEOUT = 30

def test_post_api_auth_login_with_valid_credentials():
    url = f"{BASE_URL}/api/auth/login"
    payload = {
        "email": "admin@test.com",
        "password": "adminpassword"
    }
    headers = {
        "Content-Type": "application/json"
    }

    # Since the password is not provided in PRD or instructions,
    # assuming a known password for the admin@test.com user for test purpose.
    # Adjust 'adminpassword' as per your actual test credentials.

    try:
        response = requests.post(url, json=payload, headers=headers, timeout=TIMEOUT)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        assert False, f"Request failed: {e}"

    assert response.status_code == 200, f"Expected status code 200 but got {response.status_code}"

    json_response = response.json()
    assert "token" in json_response or "access_token" in json_response, "JWT token not found in response"

    token = json_response.get("token") or json_response.get("access_token")
    assert isinstance(token, str) and len(token) > 0, "JWT token is empty or invalid"

test_post_api_auth_login_with_valid_credentials()