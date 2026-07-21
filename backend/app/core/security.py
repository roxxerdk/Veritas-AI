import hashlib
import os
from datetime import datetime, timedelta, timezone
from typing import Any, Union
import jwt

from app.config.settings import settings

ALGORITHM = "HS256"


def get_password_hash(password: str) -> str:
    """Hashes a password using PBKDF2-HMAC-SHA256 with a random salt."""
    salt = os.urandom(16)
    pwd_hash = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt,
        iterations=100000
    )
    return f"{salt.hex()}:{pwd_hash.hex()}"


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifies a plain password against its hashed representation."""
    try:
        salt_hex, hash_hex = hashed_password.split(":")
        salt = bytes.fromhex(salt_hex)
        expected_hash = bytes.fromhex(hash_hex)
        pwd_hash = hashlib.pbkdf2_hmac(
            "sha256",
            plain_password.encode("utf-8"),
            salt,
            iterations=100000
        )
        return pwd_hash == expected_hash
    except Exception:
        return False


def create_access_token(subject: Union[str, Any], expires_delta: timedelta = None) -> str:
    """Generates a secure JWT access token."""
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode = {"exp": expire, "sub": str(subject)}
    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET, algorithm=ALGORITHM)
    return encoded_jwt


def decode_access_token(token: str) -> Union[str, None]:
    """Decodes a JWT access token and returns the subject (user ID)."""
    try:
        decoded_token = jwt.decode(token, settings.JWT_SECRET, algorithms=[ALGORITHM])
        return decoded_token.get("sub")
    except jwt.PyJWTError:
        return None
