import requests
import json
import os

BASE_URL = "http://localhost:8001"

def get_tokens():
    # Register/Login Admin
    admin_payload = {
        "email": "admin@test.com",
        "password": "password123",
        "display_name": "Admin User"
    }
    
    print("Attempting to register admin...")
    try:
        resp = requests.post(f"{BASE_URL}/api/auth/register", json=admin_payload)
        print(f"Register admin status: {resp.status_code}")
    except Exception as e:
        print(f"Register admin error: {e}")

    print("Logging in admin...")
    try:
        resp = requests.post(f"{BASE_URL}/api/auth/login", json={"email": "admin@test.com", "password": "password123"})
        if resp.status_code in [200, 201]:
            admin_token = resp.json().get("access_token")
            print(f"Admin Token: {admin_token}")
        else:
            print(f"Admin login failed: {resp.status_code} {resp.text}")
    except Exception as e:
        print(f"Admin login error: {e}")

    # Register/Login Participant
    part_payload = {
        "email": "participant@test.com",
        "password": "password123",
        "display_name": "Participant User"
    }
    print("\nAttempting to register participant...")
    try:
        resp = requests.post(f"{BASE_URL}/api/auth/register", json=part_payload)
        print(f"Register participant status: {resp.status_code}")
    except Exception as e:
        print(f"Register participant error: {e}")

    print("Logging in participant...")
    try:
        resp = requests.post(f"{BASE_URL}/api/auth/login", json={"email": "participant@test.com", "password": "password123"})
        if resp.status_code in [200, 201]:
            part_token = resp.json().get("access_token")
            print(f"Participant Token: {part_token}")
        else:
            print(f"Participant login failed: {resp.status_code} {resp.text}")
    except Exception as e:
        print(f"Participant login error: {e}")

if __name__ == "__main__":
    get_tokens()
