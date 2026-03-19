import requests

BASE_URL = "http://localhost:8001"
TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbkB0ZXN0LmNvbSIsImV4cCI6MTc3Mzk4NjE3M30.0yfeSYzVT0s1KKpSldMA9bbAHT8tQWU1Ew2VvUAnGgk"
HEADERS = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json"
}

def test_update_role():
    try:
        # Step 1: Get list of profiles to get a target user to update
        resp_profiles = requests.get(f"{BASE_URL}/api/profiles", headers=HEADERS, timeout=30)
        assert resp_profiles.status_code == 200, f"Failed to list profiles, status {resp_profiles.status_code}"
        profiles = resp_profiles.json()
        assert isinstance(profiles, list) and len(profiles) > 0, "Profiles list is empty"

        # Pick the first profile that is not the admin itself - so skip the one with email admin@test.com (from token sub)
        target_profile = None
        for p in profiles:
            if "email" in p and p["email"].lower() != "admin@test.com":
                target_profile = p
                break
        if not target_profile:
            # If all are admins or no other user, create a new user to update role on
            # Register new user
            import uuid
            new_email = f"user_{uuid.uuid4().hex[:8]}@test.com"
            password = "TestPass123!"
            register_payload = {"email": new_email, "password": password}
            r_register = requests.post(f"{BASE_URL}/api/auth/register", json=register_payload, timeout=30)
            assert r_register.status_code == 201, f"User register failed with {r_register.status_code}"
            new_user = r_register.json()
            user_id = new_user.get("id")
            assert user_id, "No user id from register response"

            # Login to get token to call /api/auth/me or /api/profiles if needed
            r_login = requests.post(f"{BASE_URL}/api/auth/login", json=register_payload, timeout=30)
            assert r_login.status_code == 200, f"User login failed with {r_login.status_code}"
            user_token = r_login.json().get("access_token") or r_login.json().get("token")
            assert user_token, "No token received on login"

            # Use admin HEADERS to PATCH profile of created user_id
            target_profile = {"id": user_id}

        target_user_id = target_profile["id"]

        # Step 2: Update role to "moderator"
        patch_payload = {"role": "moderator"}
        resp_patch = requests.patch(f"{BASE_URL}/api/profiles/{target_user_id}", headers=HEADERS, json=patch_payload, timeout=30)
        assert resp_patch.status_code == 200, f"Failed to update role, status {resp_patch.status_code}"
        updated_profile = resp_patch.json()
        assert updated_profile.get("role") == "moderator", f"Role not updated correctly: {updated_profile.get('role')}"

    finally:
        # Cleanup: revert role to participant if possible
        try:
            if 'target_user_id' in locals():
                revert_payload = {"role": "participant"}
                requests.patch(f"{BASE_URL}/api/profiles/{target_user_id}", headers=HEADERS, json=revert_payload, timeout=30)
        except Exception:
            pass

test_update_role()