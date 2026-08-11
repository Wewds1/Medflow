"""
Decentralized Token Verification Script for MedFlow.

This script demonstrates the core security property of asymmetric signing (RS256):
A token issued by the Auth service can be verified by ANY other service using only
the public key, without needing to contact the Auth service or hold the private key.

Usage:
    python services\auth\verify_token.py <jwt_token>
"""
import sys
import os
from jose import jwt, JWTError
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))

def verify_token(token: str):
    # Load the public key
    public_key_path = os.getenv("RSA_PUBLIC_KEY_PATH", "public.pem")
    try:
        with open(public_key_path, "rb") as key_file:
            public_key = key_file.read()
    except FileNotFoundError:
        print(f"Error: Public key not found at {public_key_path}")
        return

    try:
        # Decode and verify the token using RS256 and the public key
        payload = jwt.decode(token, public_key, algorithms=["RS256"])

        print("\n--- Token Verified Successfully ---")
        print(f"User: {payload.get('sub')}")
        print(f"Permissions: {payload.get('permissions', [])}")
        print(f"Expires at: {payload.get('exp')}")
        print("----------------------------------\n")

    except JWTError as e:
        print(f"Error: Token verification failed. {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python verify_token.py <token>")
        sys.exit(1)

    token_to_verify = sys.argv[1]
    verify_token(token_to_verify)
