import requests

def test_user_profile():
    base_url = "http://localhost:8001"
    token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbkB0ZXN0LmNvbSIsImV4cCI6MTc3Mzk4NjE3M30.0yfeSYzVT0s1KKpSldMA9bbAHT8tQWU1Ew2VvUAnGgk"
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json"
    }

    try:
        response = requests.get(f"{base_url}/api/auth/me", headers=headers, timeout=30)
        assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"
        data = response.json()
        # Validate some expected keys in the user profile response
        assert "email" in data, "Response JSON does not contain 'email'"
        assert "role" in data, "Response JSON does not contain 'role'"
        assert data["email"].lower() == "admin@test.com", f"Email mismatch, got {data['email']}"
    except requests.RequestException as e:
        assert False, f"Request failed: {e}"

test_user_profile()