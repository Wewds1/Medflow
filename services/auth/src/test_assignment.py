import urllib.request
import json

BASE_URL = "http://localhost:8000"

def test_role_assignment():
    # 1. Login as admin
    data = json.dumps({"username": "admin", "password": "admin123"}).encode("utf-8")
    req = urllib.request.Request(f"{BASE_URL}/token", data=data, headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req) as res:
            token = json.loads(res.read().decode()).get("access_token")
            print("Login successful")
    except Exception as e:
        print(f"Login failed: {e}")
        return

    # 2. Assign role to doctor1 (ID 4)
    data = json.dumps({"role_id": 6}).encode("utf-8")
    req = urllib.request.Request(f"{BASE_URL}/users/4/roles", data=data,
                                headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req) as res:
            print(f"Assign Role Response ({res.getcode()}): {res.read().decode()}")
    except Exception as e:
        print(f"Assign Role failed: {e}")

if __name__ == "__main__":
    test_role_assignment()
