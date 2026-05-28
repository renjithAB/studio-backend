from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field, validator
from app.core.validators import validate_code_format

# ──────────────────────────────────────────────────────────────────────────────
# Base Task Template Schema – shared fields for all operations
# ──────────────────────────────────────────────────────────────────────────────
class TaskTemplateBase(BaseModel):
    code: str
    name: str
    description: Optional[str] = None
    domain_code: str
    is_active: bool = True

# ──────────────────────────────────────────────────────────────────────────────
# Create Task Template – used when creating a new task template
# ──────────────────────────────────────────────────────────────────────────────
class TaskTemplateCreate(TaskTemplateBase):
    applies_to_templates: Optional[List[str]] = []

    @validator('code')
    def validate_code(cls, v):
        return validate_code_format(v)

# ──────────────────────────────────────────────────────────────────────────────
# Update Task Template – all fields optional for partial updates
# ──────────────────────────────────────────────────────────────────────────────
class TaskTemplateUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    domain_code: Optional[str] = None
    is_active: Optional[bool] = None
    code: Optional[str] = None
    applies_to_templates: Optional[List[str]] = None

    @validator('code')
    def validate_code(cls, v):
        if v is None:
            return v
        return validate_code_format(v)

# ──────────────────────────────────────────────────────────────────────────────
# Task Template DB / Response Model
# ──────────────────────────────────────────────────────────────────────────────
class TaskTemplateOut(TaskTemplateBase):
    id: int = Field(..., ge=1000, description="Task Template ID must be 1000 or greater")
    applies_to_templates: List[str] = []
    created_at: datetime
    updated_at: Optional[datetime] = None
    created_by: Optional[int] = Field(None, ge=1000, description="User ID must be 1000 or greater")
    updated_by: Optional[int] = Field(None, ge=1000, description="User ID must be 1000 or greater")

    @validator('id', 'created_by', 'updated_by')
    def validate_ids(cls, v):
        if v is not None and v < 1000:
            raise ValueError('ID must be 1000 or greater')
        return v

    class Config:
        from_attributes = True
