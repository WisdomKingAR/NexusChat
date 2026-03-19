import requests
import uuid

BASE_URL = "http://localhost:8001"
AUTH_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbkB0ZXN0LmNvbSIsImV4cCI6MTc3Mzk4NjE3M30.0yfeSYzVT0s1KKpSldMA9bbAHT8tQWU1Ew2VvUAnGgk"
HEADERS = {
    "Authorization": f"Bearer {AUTH_TOKEN}",
    "Content-Type": "application/json"
}

def test_user_registration():
    url = f"{BASE_URL}/api/auth/register"
    unique_email = f"testuser_{uuid.uuid4().hex}@example.com"
    payload = {
        "email": unique_email,
        "password": "StrongPassw0rd!"
    }
    response = requests.post(url, json=payload, timeout=30)
    try:
        assert response.status_code == 201, f"Expected 201, got {response.status_code}, body: {response.text}"
        data = response.json()
        assert "id" in data, "Response JSON missing 'id'"
        assert isinstance(data["id"], (str, int)), "'id' should be str or int"
    finally:
        pass

if __name__ == "__main__":
    test_user_registration()
