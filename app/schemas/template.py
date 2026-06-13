from typing import Optional, List, Any
from datetime import datetime
from pydantic import BaseModel, Field, validator
from app.core.validators import validate_code_format

# ──────────────────────────────────────────────────────────────────────────────
# Base Template Schema – shared fields for all operations
# ──────────────────────────────────────────────────────────────────────────────
class TemplateBase(BaseModel):
    code: str
    name: str
    description: Optional[str] = None
    thumbnail_url: Optional[str] = None
    tag: Optional[str] = None
    domain: Optional[str] = None
    has_episode: bool = False
    is_active: bool = True
    applicable_templates: Optional[str] = None

# ──────────────────────────────────────────────────────────────────────────────
# Create Template – used when creating a new template
# ──────────────────────────────────────────────────────────────────────────────
class TemplateCreate(TemplateBase):
    @validator('code')
    def validate_code(cls, v):
        return validate_code_format(v)

# ──────────────────────────────────────────────────────────────────────────────
# Update Template – all fields optional for partial updates
# ──────────────────────────────────────────────────────────────────────────────
class TemplateUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    thumbnail_url: Optional[str] = None
    tag: Optional[str] = None
    domain: Optional[str] = None
    code: Optional[str] = None
    has_episode: Optional[bool] = None
    is_active: Optional[bool] = None
    applicable_templates: Optional[str] = None

    @validator('code')
    def validate_code(cls, v):
        if v is None:
            return v
        return validate_code_format(v)

# ──────────────────────────────────────────────────────────────────────────────
# Template in DB / Response Model – includes database-generated fields
# ──────────────────────────────────────────────────────────────────────────────
class TemplateOut(TemplateBase):
    id: int = Field(..., ge=1000, description="Template ID must be 1000 or greater")
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    created_by: Optional[int] = Field(None, ge=1000, description="User ID must be 1000 or greater")
    updated_by: Optional[int] = Field(None, ge=1000, description="User ID must be 1000 or greater")

    # Validate all ID fields (optional, remove if not needed)
    @validator('id', 'created_by', 'updated_by')
    def validate_ids(cls, v):
        if v is not None and v < 1000:
            raise ValueError('ID must be 1000 or greater')
        return v

    class Config:
        from_attributes = True



class TaskTemplateOut(BaseModel):
    name: str
    code: str

    class Config:
        from_attributes = True