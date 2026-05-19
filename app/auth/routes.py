from fastapi import APIRouter, Depends, HTTPException, Response, Request, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from datetime import datetime
from typing import Any
import bcrypt

from app.database import get_db
from app.models.users import User
from app.schemas.users import UserLogin, TokenResponse, CSRFTokenResponse
from app.core.security import (
    create_session_token, 
    generate_csrf_token
)
from app.core.ratelimit import limiter, login_tracker
from app.config import get_settings

router = APIRouter(prefix="/auth", tags=["authentication"])
settings = get_settings()

@router.get("/csrf", response_model=CSRFTokenResponse)
@limiter.limit("30/minute")  # Rate limit for CSRF token generation
async def get_csrf_token(request: Request, response: Response):
    """Generate and return a CSRF token."""
    csrf_token = generate_csrf_token()
    
    response.set_cookie(
        key=settings.CSRF_COOKIE_NAME,
        value=csrf_token,
        httponly=settings.CSRF_COOKIE_HTTPONLY,
        secure=settings.CSRF_COOKIE_SECURE,
        samesite="lax",
        max_age=3600,
        path="/"
    )
    
    return CSRFTokenResponse(csrf_token=csrf_token)

@router.post("/login", response_model=TokenResponse)
@limiter.limit(settings.LOGIN_RATE_LIMIT if settings.RATE_LIMIT_ENABLED else "1000/minute")
async def login(
    request: Request,
    response: Response,
    login_data: UserLogin,
    db: Session = Depends(get_db)
):
    """
    Authenticate user and create session with rate limiting and account locking.
    """
    # Get client identifier (IP address or email for more granular control)
    client_ip = request.client.host
    email = login_data.email
    
    # Check if this email or IP is locked
    is_locked, locked_until = login_tracker.is_locked(email)
    if is_locked:
        remaining_seconds = int((locked_until - datetime.utcnow()).total_seconds())
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail={
                "message": "Account temporarily locked due to too many failed attempts",
                "locked_until": locked_until.isoformat(),
                "remaining_seconds": remaining_seconds,
                "retry_after": remaining_seconds
            }
        )
    
    # Find user by email
    user = db.query(User).filter(
        User.email == login_data.email,
        User.is_deleted == False,
        User.is_active == True
    ).first()
    
    # Track failed attempt if user not found
    if not user:
        # Record failed attempt
        attempts = login_tracker.record_failed_attempt(email)
        remaining = settings.MAX_LOGIN_ATTEMPTS - attempts
        
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "message": "Invalid email or password",
                "remaining_attempts": remaining,
                "will_lock_after": settings.MAX_LOGIN_ATTEMPTS - attempts
            }
        )
    
    # Verify password using direct bcrypt
    try:
        password_bytes = login_data.password.encode('utf-8')
        hash_bytes = user.private_key.encode('utf-8') if isinstance(user.private_key, str) else user.private_key
        is_password_valid = bcrypt.checkpw(password_bytes, hash_bytes)
    except Exception as e:
        print(f"Password verification error: {e}")
        is_password_valid = False
    
    if not is_password_valid:
        # Record failed attempt
        attempts = login_tracker.record_failed_attempt(email)
        remaining = settings.MAX_LOGIN_ATTEMPTS - attempts
        
        error_detail = {
            "message": "Invalid email or password",
            "remaining_attempts": remaining
        }
        
        # Check if this attempt will trigger lockout
        if attempts >= settings.MAX_LOGIN_ATTEMPTS:
            lockout_minutes = settings.LOGIN_LOCKOUT_TIME
            error_detail["message"] = f"Too many failed attempts. Account locked for {lockout_minutes} minutes."
            error_detail["locked"] = True
            error_detail["lockout_minutes"] = lockout_minutes
        
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=error_detail
        )
    
    # Successful login - clear failed attempts
    login_tracker.record_successful_attempt(email)
    
    # Update last login
    user.last_login_at = datetime.utcnow()
    db.commit()
    
    # Create session token
    session_token = create_session_token(str(user.id))
    
    # Set session cookie
    response.set_cookie(
        key=settings.SESSION_COOKIE_NAME,
        value=session_token,
        httponly=True,
        secure=settings.CSRF_COOKIE_SECURE,
        samesite="lax",
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        path="/"
    )
    
    return TokenResponse(
        access_token=session_token,
        user=user
    )

@router.post("/logout")
async def logout(response: Response):
    """Logout user by clearing session cookie."""
    response.delete_cookie(key=settings.SESSION_COOKIE_NAME, path="/")
    response.delete_cookie(key=settings.CSRF_COOKIE_NAME, path="/")
    return {"message": "Successfully logged out"}

@router.get("/verify")
@limiter.limit("30/minute")
async def verify_session(request: Request, db: Session = Depends(get_db)):
    """Verify if the current session is valid."""
    session_token = request.cookies.get(settings.SESSION_COOKIE_NAME)
    
    if not session_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated"
        )
    
    # Add JWT verification here if needed
    
    return {"valid": True, "message": "Session is valid"}

@router.get("/attempts/{email}")
async def get_login_attempts(email: str):
    """Get remaining login attempts for an email (useful for frontend)."""
    remaining = login_tracker.get_remaining_attempts(email)
    is_locked, locked_until = login_tracker.is_locked(email)
    
    return {
        "email": email,
        "remaining_attempts": remaining,
        "is_locked": is_locked,
        "locked_until": locked_until.isoformat() if locked_until else None
    }