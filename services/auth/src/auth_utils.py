import os
from datetime import datetime, timedelta, timezone
from typing import List, Optional
from jose import jwt, JWTError
import bcrypt
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "RS256" # Using Asymmetric signing as per plan

def verify_password(plain_password: str, hashed_password: str):
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

def get_password_hash(password: str):
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})

    # Load private key from RSA_PRIVATE_KEY_PATH in .env
    key_path = os.getenv("RSA_PRIVATE_KEY_PATH", "private.pem")
    try:
        with open(key_path, "rb") as key_file:
            private_key = key_file.read()
    except FileNotFoundError:
        raise RuntimeError(f"RSA private key not found at {key_path}. Please check your .env file.")

    return jwt.encode(to_encode, private_key, algorithm=ALGORITHM)


def decode_access_token(token: str, public_key: str):
    try:
        payload = jwt.decode(token, public_key, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None
