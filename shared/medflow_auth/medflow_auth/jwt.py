from datetime import datetime, timedelta, timezone
from typing import List, Optional, Any
from jose import jwt, JWTError

ALGORITHM = "RS256"

def create_access_token(data: dict, private_key: bytes, expires_delta: Optional[timedelta] = None) -> str:
    """
    Creates a JWT access token signed with an RSA private key.
    """
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})

    return jwt.encode(to_encode, private_key, algorithm=ALGORITHM)

def decode_access_token(token: str, public_key: bytes) -> Optional[Any]:
    """
    Decodes a JWT access token using an RSA public key.
    """
    try:
        payload = jwt.decode(token, public_key, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None
