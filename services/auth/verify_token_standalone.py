import os
from datetime import timedelta
from medflow_auth.jwt import create_access_token, decode_access_token

def main():
    # 1. Setup keys (simulating the Auth service)
    # In a real scenario, only the Auth service has the private key
    private_key_path = "private.pem"
    public_key_path = "public.pem"

    try:
        with open(private_key_path, "rb") as f:
            private_key = f.read()
        with open(public_key_path, "rb") as f:
            public_key = f.read()
    except FileNotFoundError as e:
        print(f"Error: Missing keys. Ensure private.pem and public.pem are in the current directory. {e}")
        return

    # 2. Create a token (Simulating Auth Service login)
    test_data = {"sub": "test_user", "permissions": ["encounters:write", "inventory:dispense"]}
    token = create_access_token(test_data, private_key, expires_delta=timedelta(minutes=15))
    print(f"Generated Token: {token}\n")

    # 3. Verify the token (Simulating ANY other service)
    # This part ONLY uses the public key and the shared library
    print("Verifying token using ONLY the public key...")
    payload = decode_access_token(token, public_key)

    if payload:
        print("✅ Success! Token verified.")
        print(f"Payload: {payload}")
        assert payload["sub"] == "test_user"
        assert "encounters:write" in payload["permissions"]
    else:
        print("❌ Failure: Token could not be verified.")

if __name__ == "__main__":
    main()
