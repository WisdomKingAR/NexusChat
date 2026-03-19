import requests
import uuid

BASE_URL = "http://localhost:8001"
TIMEOUT = 30

def test_post_api_auth_register_new_user():
    url = f"{BASE_URL}/api/auth/register"
    unique_email = f"testuser_{uuid.uuid4().hex[:8]}@example.com"
    payload = {
        "email": unique_email,
        "password": "ValidPass123!",
        "display_name": "Test User"
    }
    try:
        response = requests.post(url, json=payload, timeout=TIMEOUT)
        assert response.status_code == 201, f"Expected 201 Created, got {response.status_code}"
        data = response.json()
        assert "id" in data, "Response JSON should contain new user id"
        user_id = data["id"]
    except requests.RequestException as e:
        assert False, f"Request failed: {e}"

test_post_api_auth_register_new_user()