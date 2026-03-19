import requests
import sys

BASE_URL = "http://localhost:8001"
ADMIN_EMAIL = "admin@test.com"
ADMIN_PASS = "AdminPassword123!"
ADMIN_NAME = "System Admin"

def setup():
    print(f"Setting up admin user: {ADMIN_EMAIL}")
    headers = {"Content-Type": "application/json"}
    
    # 1. Try to register
    payload = {
        "email": ADMIN_EMAIL,
        "password": ADMIN_PASS,
        "display_name": ADMIN_NAME
    }
    
    try:
        resp = requests.post(f"{BASE_URL}/api/auth/register", json=payload, headers=headers, timeout=10)
        if resp.status_code == 201:
            print("Admin user registered successfully (and should have admin role).")
            return True
        elif resp.status_code == 400:
            print("Admin user already exists. Attempting login to verify...")
            resp_login = requests.post(f"{BASE_URL}/api/auth/login", json={"email": ADMIN_EMAIL, "password": ADMIN_PASS}, headers=headers, timeout=10)
            if resp_login.status_code == 201:
                print("Login successful. Admin set up.")
                return True
            else:
                print(f"Login failed for existing admin: {resp_login.status_code} - {resp_login.text}")
                return False
        else:
            print(f"Unexpected status code during registration: {resp.status_code} - {resp.text}")
            return False
    except Exception as e:
        print(f"Error during admin setup: {e}")
        return False

if __name__ == "__main__":
    if setup():
        sys.exit(0)
    else:
        sys.exit(1)
