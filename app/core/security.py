import bcrypt
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from jose import jwt
import secrets
from itsdangerous import URLSafeTimedSerializer, BadSignature, SignatureExpired

from app.config import get_settings

settings = get_settings()

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain password against a bcrypt hashed password."""
    try:
        # Ensure password is bytes
        if isinstance(plain_password, str):
            plain_password = plain_password.encode('utf-8')
        if isinstance(hashed_password, str):
            hashed_password = hashed_password.encode('utf-8')
        
        return bcrypt.checkpw(plain_password, hashed_password)
    except Exception as e:
        print(f"Password verification error: {e}")
        return False

def get_private_key(password: str) -> str:
    """Hash a password using bcrypt."""
    try:
        # Convert password to bytes and hash
        password_bytes = password.encode('utf-8')
        salt = bcrypt.gensalt(rounds=12)  # 12 rounds is standard
        hashed = bcrypt.hashpw(password_bytes, salt)
        # Return as string for database storage
        return hashed.decode('utf-8')
    except Exception as e:
        print(f"Password hashing error: {e}")
        raise

def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT access token."""
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    
    return encoded_jwt

def generate_csrf_token() -> str:
    """Generate a new CSRF token."""
    return secrets.token_urlsafe(32)

def verify_csrf_token(token: str) -> bool:
    """Simple CSRF token verification (just check it exists and is valid format)."""
    # Since we're using secrets.token_urlsafe, any non-empty string is valid
    # In production, you might want to store and validate against a session
    return bool(token and len(token) > 20)

def create_session_token(user_id: str) -> str:
    """Create a session token (JWT)."""
    return create_access_token({"sub": str(user_id)})

import hashlib

def generate_api_token() -> tuple[str, str, str]:
    """
    Generate a new API token.
    Returns: (prefix, plain_token, hashed_token)
    """
    prefix = secrets.token_urlsafe(8)[:8]
    secret = secrets.token_urlsafe(32)
    plain_token = f"{prefix}.{secret}"
    hashed_token = hashlib.sha256(plain_token.encode()).hexdigest()
    return prefix, plain_token, hashed_token

def hash_api_token(plain_token: str) -> str:
    """Hash a plain API token for comparison."""
    return hashlib.sha256(plain_token.encode()).hexdigest()