"""
Web authentication and JWT utilities.
@Architecture-Map: [WEB-AUTH]
"""
from typing import Optional
from src.core.config import ENCRYPTION_KEY
import jwt
from datetime import datetime, timedelta, timezone

ALGORITHM = "HS256"

def create_jwt_token(data: dict) -> str:
    """Creates a signed JWT token containing user data."""
    to_encode = data.copy()
    # 7 days expiration
    expire = datetime.now(timezone.utc) + timedelta(days=7)
    to_encode.update({"exp": expire})
    # We reuse the existing ENCRYPTION_KEY for JWT signing. 
    # In a massive production app we'd use a separate JWT_SECRET, but this is fine.
    encoded_jwt = jwt.encode(to_encode, ENCRYPTION_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def decode_jwt_token(token: str) -> Optional[dict]:
    """Decodes and verifies a JWT token. Returns None if invalid or expired."""
    try:
        decoded_data = jwt.decode(token, ENCRYPTION_KEY, algorithms=[ALGORITHM])
        return decoded_data
    except jwt.PyJWTError:
        return None