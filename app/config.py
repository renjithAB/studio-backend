from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import Optional

class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "postgresql://user:pass@localhost/tenant_db"
    
    # Security
    SECRET_KEY: str = "your-secret-key-here-change-in-production"
    CSRF_SECRET: str = "csrf-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    SESSION_COOKIE_NAME: str = "session"
    
    # CSRF Settings
    CSRF_COOKIE_NAME: str = "csrf_token"
    CSRF_HEADER_NAME: str = "X-CSRF-Token"
    CSRF_COOKIE_SECURE: bool = False
    CSRF_COOKIE_HTTPONLY: bool = False
    
    # Rate Limiting
    RATE_LIMIT_ENABLED: bool = True
    LOGIN_RATE_LIMIT: str = "5/minute"  # 5 attempts per minute per IP
    LOGIN_LOCKOUT_TIME: int = 15  # minutes
    MAX_LOGIN_ATTEMPTS: int = 5
    
    # Redis (for distributed rate limiting)
    REDIS_URL: Optional[str] = None  # e.g., "redis://localhost:6379/0"
    
    # CORS
    CORS_ORIGINS: list = ["http://localhost:3000"]
    
    class Config:
        env_file = ".env"

@lru_cache()
def get_settings():
    return Settings()