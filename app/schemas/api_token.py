from typing import Optional
from pydantic import BaseModel
from datetime import datetime

class ApiTokenBase(BaseModel):
    name: str

class ApiTokenCreate(ApiTokenBase):
    pass

class ApiTokenResponse(ApiTokenBase):
    id: int
    prefix: str
    is_active: bool
    created_at: datetime
    last_used_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class ApiTokenWithPlaintext(ApiTokenResponse):
    token: str  # Only returned once upon creation
