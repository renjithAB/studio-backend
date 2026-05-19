from pydantic import BaseModel, EmailStr, Field, validator
from datetime import datetime
from typing import Optional, Dict, Any

class UserBase(BaseModel):
    email: EmailStr
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    enable: bool = True

class UserCreate(UserBase):
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(UserBase):
    id: int = Field(..., ge=1000, description="User ID must be 1000 or greater")
    type: Optional[str] = None
    # role: Optional[int] = Field(None, ge=1000, description="Role ID must be 1000 or greater")
    # permission: Optional[int] = Field(None, ge=1000, description="Permission ID must be 1000 or greater")
    is_super: bool
    created_at: datetime
    created_by: Optional[int] = Field(None, ge=1000, description="Created by user ID must be 1000 or greater")
    updated_by: Optional[int] = Field(None, ge=1000, description="Updated by user ID must be 1000 or greater")
    last_login_at: Optional[datetime] = None
    preferences: Dict[str, Any] = {}
    
    @validator('id')
    def validate_id(cls, v):
        if v < 1000:
            raise ValueError('User ID must be 1000 or greater')
        return v
    
    @validator('created_by', 'updated_by')
    def validate_user_ids(cls, v):
        if v is not None and v < 1000:
            raise ValueError('User ID must be 1000 or greater')
        return v
    
    class Config:
        from_attributes = True

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse

class CSRFTokenResponse(BaseModel):
    csrf_token: str
    message: str = "CSRF token generated successfully"