import os
from datetime import datetime, timedelta, timezone
from typing import List, Optional
from jose import jwt, JWTError
from passlib.context import CryptContext
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="legacy")
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "RS256" # Using Asymmetric signing as per plan

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    
    #  load the private key from RSA_PRIVATE_KEY_PATH
    private_key = os.getenv("RSA_PRIVATE_KEY") or SECRET_KEY 
    
    return jwt.encode(to_encode, private_key, algorithm=ALGORITHM)

def decode_access_token(token: str, public_key: str):
    try:
        payload = jwt.decode(token, public_key, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None
