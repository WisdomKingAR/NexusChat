import pytest
from fastapi.testclient import TestClient
from unittest.mock import MagicMock, AsyncMock, patch
import os

# Mock environment variables before importing app
os.environ["MONGO_URL"] = "mongodb://localhost:27017"
os.environ["JWT_SECRET"] = "a" * 32

# Patch Motor client before importing server
with patch("motor.motor_asyncio.AsyncIOMotorClient"):
    from backend.server import app, db

client = TestClient(app)

class MockAsyncIterator:
    def __init__(self, items):
        self.items = items
        self.index = 0

    def __aiter__(self):
        return self

    async def __anext__(self):
        if self.index < len(self.items):
            result = self.items[self.index]
            self.index += 1
            return result
        else:
            raise StopAsyncIteration

@pytest.mark.asyncio
async def test_api_users_no_email_exposure():
    """Verify that /api/users DOES NOT return email anymore."""
    # Mock database response for find()
    mock_users = [
        {
            "_id": "65f1a2b3c4d5e6f7a8b9c0d1",
            "email": "victim@example.com",
            "display_name": "Victim",
            "role": "participant",
            "created_at": "2024-01-01T00:00:00"
        }
    ]

    mock_cursor = MockAsyncIterator(mock_users)

    with patch("backend.server.db.users.find", return_value=mock_cursor):
        from backend.server import get_current_user
        app.dependency_overrides[get_current_user] = lambda: {
            "id": "65f1a2b3c4d5e6f7a8b9c0d2",
            "email": "attacker@example.com",
            "display_name": "Attacker",
            "role": "participant"
        }

        response = client.get("/api/users")
        app.dependency_overrides = {}

        assert response.status_code == 200
        data = response.json()

        for user in data:
            # Check that email is NOT in the response
            assert "email" not in user

@pytest.mark.asyncio
async def test_api_auth_me_still_has_email():
    """Verify that /api/auth/me still returns the current user's email."""
    from backend.server import get_current_user
    app.dependency_overrides[get_current_user] = lambda: {
        "id": "65f1a2b3c4d5e6f7a8b9c0d2",
        "email": "attacker@example.com",
        "display_name": "Attacker",
        "role": "participant",
        "created_at": "2024-01-01T00:00:00"
    }

    response = client.get("/api/auth/me")
    app.dependency_overrides = {}

    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "attacker@example.com"
