from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi import Request, HTTPException, status
from datetime import datetime, timedelta
from typing import Optional, Dict
import redis
import json
from app.config import get_settings

settings = get_settings()

# Initialize Redis if URL is provided
redis_client = None
if settings.REDIS_URL:
    try:
        redis_client = redis.from_url(settings.REDIS_URL)
    except Exception as e:
        print(f"Redis connection failed: {e}, using in-memory storage")

# In-memory fallback storage (for development)
login_attempts: Dict[str, dict] = {}

class LoginTracker:
    """Tracks login attempts and implements temporary locking."""
    
    def __init__(self, redis_client=None):
        self.redis = redis_client
        self.max_attempts = settings.MAX_LOGIN_ATTEMPTS
        self.lockout_minutes = settings.LOGIN_LOCKOUT_TIME
    
    def _get_key(self, identifier: str) -> str:
        """Get Redis key for an identifier."""
        return f"login_attempts:{identifier}"
    
    def record_failed_attempt(self, identifier: str) -> int:
        """
        Record a failed login attempt.
        Returns the current number of attempts.
        """
        now = datetime.utcnow()
        
        if self.redis:
            # Use Redis for distributed storage
            key = self._get_key(identifier)
            pipe = self.redis.pipeline()
            
            # Increment attempt count and set expiry
            pipe.incr(key)
            pipe.expire(key, self.lockout_minutes * 60)
            result = pipe.execute()
            return result[0]  # Current count
        else:
            # Use in-memory storage
            if identifier not in login_attempts:
                login_attempts[identifier] = {
                    'count': 0,
                    'first_attempt': now,
                    'locked_until': None
                }
            
            data = login_attempts[identifier]
            
            # Check if lockout period has expired
            if data['locked_until'] and now > data['locked_until']:
                # Reset if lockout expired
                data['count'] = 0
                data['locked_until'] = None
                data['first_attempt'] = now
            
            data['count'] += 1
            
            # If this is the first attempt in a new series, record the time
            if data['count'] == 1:
                data['first_attempt'] = now
            
            return data['count']
    
    def record_successful_attempt(self, identifier: str):
        """Clear failed attempts record after successful login."""
        if self.redis:
            key = self._get_key(identifier)
            self.redis.delete(key)
        else:
            if identifier in login_attempts:
                del login_attempts[identifier]
    
    def is_locked(self, identifier: str) -> tuple[bool, Optional[datetime]]:
        """
        Check if an identifier is locked.
        Returns (is_locked, locked_until)
        """
        now = datetime.utcnow()
        
        if self.redis:
            key = self._get_key(identifier)
            count = self.redis.get(key)
            
            if count and int(count) >= self.max_attempts:
                # Get TTL of the key
                ttl = self.redis.ttl(key)
                if ttl > 0:
                    locked_until = now + timedelta(seconds=ttl)
                    return True, locked_until
            return False, None
        else:
            data = login_attempts.get(identifier)
            if not data:
                return False, None
            
            # Check if locked due to too many attempts
            if data['count'] >= self.max_attempts:
                # Calculate lockout end time
                lockout_end = data['first_attempt'] + timedelta(minutes=self.lockout_minutes)
                
                if now < lockout_end:
                    return True, lockout_end
                else:
                    # Lockout expired, reset
                    del login_attempts[identifier]
                    return False, None
            
            return False, None
    
    def get_remaining_attempts(self, identifier: str) -> int:
        """Get remaining attempts before lockout."""
        if self.redis:
            key = self._get_key(identifier)
            count = self.redis.get(key)
            current = int(count) if count else 0
            return max(0, self.max_attempts - current)
        else:
            data = login_attempts.get(identifier)
            if not data:
                return self.max_attempts
            
            # Check if lockout is active
            now = datetime.utcnow()
            if data.get('locked_until') and now < data['locked_until']:
                return 0
            
            return max(0, self.max_attempts - data['count'])

# Initialize limiter
limiter = Limiter(key_func=get_remote_address)

# Initialize login tracker
login_tracker = LoginTracker(redis_client)