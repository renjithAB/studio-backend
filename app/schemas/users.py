from pydantic import BaseModel, EmailStr, Field, validator
from datetime import datetime
from typing import Optional, Dict, Any, List


class PermissionResponse(BaseModel):
    id: int
    code: str
    name: str
    description: Optional[str] = None

    class Config:
        from_attributes = True


class RoleResponse(BaseModel):
    id: int
    code: str
    name: str
    description: Optional[str] = None
    permissions: List[PermissionResponse] = []

    class Config:
        from_attributes = True


class RoleCreate(BaseModel):
    code: str
    name: str
    description: Optional[str] = None
    permission_ids: List[int] = []


class RoleUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    permission_ids: Optional[List[int]] = None


class UserBase(BaseModel):
    email: EmailStr
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    is_active: bool = True


class UserListItem(BaseModel):
    id: int
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: EmailStr

    class Config:
        from_attributes = True


class UserCreate(UserBase):
    password: str
    role_id: int
    is_super: bool = False


class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    password: Optional[str] = None
    role_id: Optional[int] = None
    is_super: Optional[bool] = None
    is_active: Optional[bool] = None


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserResponse(UserBase):
    id: int = Field(..., ge=1000)
    type: Optional[str] = None
    role_id: Optional[int] = None
    role: Optional[RoleResponse] = None
    is_super: bool
    created_at: datetime
    created_by: Optional[int] = None
    updated_by: Optional[int] = None
    last_login_at: Optional[datetime] = None
    preferences: Dict[str, Any] = {}

    @validator('id')
    def validate_id(cls, v):
        if v < 1000:
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