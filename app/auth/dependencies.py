from fastapi import Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.users import User
from app.config import get_settings
from app.core.security import verify_csrf_token

settings = get_settings()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login", auto_error=False)

async def get_current_user(
    request: Request,
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme)
) -> User:
    """
    Get the current authenticated user from the session cookie or token.
    """
    # Try to get token from cookie if not in header
    if not token:
        token = request.cookies.get(settings.SESSION_COOKIE_NAME)
    
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated"
        )
    
    try:
        # Decode JWT
        payload = jwt.decode(
            token, 
            settings.SECRET_KEY, 
            algorithms=[settings.ALGORITHM]
        )
        user_id = payload.get("sub")
        
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials"
            )
        
        # Convert string to integer
        try:
            user_int_id = int(user_id)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid user ID format - must be integer"
            )
        
        # Optional: Validate ID range (>= 1000)
        if user_int_id < 1000:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid user ID - must be 1000 or greater"
            )
        
        # Get user from database
        user = db.query(User).filter(
            User.id == user_int_id,
            User.is_active == True  # Changed from is_deleted to is_active based on your schema
        ).first()
        
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found"
            )
        
        return user
        
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials"
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid user ID format: {str(e)}"
        )

def require_csrf_token(request: Request):
    """
    Dependency to require CSRF token for state-changing operations.
    """
    # Get CSRF token from header
    csrf_token_header = request.headers.get(settings.CSRF_HEADER_NAME)
    
    # Get CSRF token from cookie
    csrf_token_cookie = request.cookies.get(settings.CSRF_COOKIE_NAME)
    
    if not csrf_token_header or not csrf_token_cookie:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="CSRF token missing"
        )
    
    # Verify tokens match
    if csrf_token_header != csrf_token_cookie:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="CSRF token mismatch"
        )
    
    # Verify token is valid
    if not verify_csrf_token(csrf_token_header):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid or expired CSRF token"
        )
    
    return csrf_token_header