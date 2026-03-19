import requests
import uuid

BASE_URL = "http://localhost:8001"
REGISTER_ENDPOINT = "/api/auth/register"
TIMEOUT = 30

def test_post_api_auth_register_user_registration():
    headers = {
        "Content-Type": "application/json"
    }

    # Generate unique email for successful registration
    unique_email = f"testuser_{uuid.uuid4().hex}@example.com"
    password = "ValidPass123!"

    # Payload for registration with unique email and REQUIRED display_name
    payload = {
        "email": unique_email,
        "password": password,
        "display_name": "Test User"
    }

    # Register new user - expect 201 Created with user id in 'user' field
    response = requests.post(
        BASE_URL + REGISTER_ENDPOINT, json=payload, headers=headers, timeout=TIMEOUT)
    try:
        assert response.status_code == 201, f"Expected 201, got {response.status_code}"
        data = response.json()
        assert "user" in data, "Response JSON does not contain 'user' field"
        assert "id" in data["user"], "Response JSON user field does not contain 'id'"
    except Exception as e:
        print(f"Error during registration: {response.text}")
        raise e

    # Attempt registration with the same email again - expect 400 Bad Request with detail 'Email already registered'
    response_conflict = requests.post(
        BASE_URL + REGISTER_ENDPOINT, json=payload, headers=headers, timeout=TIMEOUT)
    assert response_conflict.status_code == 400, f"Expected 400, got {response_conflict.status_code}. Details: {response_conflict.text}"
    conflict_data = response_conflict.json()
    assert "detail" in conflict_data or "message" in conflict_data
    detail = conflict_data.get("detail", conflict_data.get("message", "")).lower()
    assert "registered" in detail or "exists" in detail

if __name__ == "__main__":
    test_post_api_auth_register_user_registration()