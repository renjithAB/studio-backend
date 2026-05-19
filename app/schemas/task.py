from typing import Optional
from pydantic import BaseModel, ConfigDict, field_validator
from app.core.validators import validate_code_format
from datetime import datetime

class TaskBase(BaseModel):
    code: str
    name: str
    thumbnail_url: Optional[str] = None
    tag: Optional[str] = None
    is_active: bool = True

class TaskCreate(TaskBase):
    @field_validator('code')
    @classmethod
    def validate_code(cls, v: str) -> str:
        return validate_code_format(v)
    project_id: int
    domain_id: Optional[int] = None
    category_id: Optional[int] = None      # now optional
    asset_id: Optional[int] = None         # now optional
    # Optional fields for other relationships
    episode_id: Optional[int] = None
    sequence_id: Optional[int] = None
    shot_id: Optional[int] = None
    library_id: Optional[int] = None
    cycle_id: Optional[int] = None
    editorial_id: Optional[int] = None
    template_id: Optional[int] = None

    @field_validator('asset_id', 'shot_id', 'domain_id')
    def check_at_least_one(cls, v, info):
        # This validator runs after individual field validation, but we need to check both.
        # We'll handle it in the CRUD to avoid complexity with Pydantic context.
        return v

class TaskUpdate(BaseModel):
    code: Optional[str] = None
    name: Optional[str] = None
    description: Optional[str] = None
    tag: Optional[str] = None
    is_active: Optional[bool] = None
    thumbnail_url: Optional[str] = None
    domain_id: Optional[int] = None
    category_id: Optional[int] = None
    asset_id: Optional[int] = None
    shot_id: Optional[int] = None
    episode_id: Optional[int] = None
    sequence_id: Optional[int] = None
    library_id: Optional[int] = None
    cycle_id: Optional[int] = None
    editorial_id: Optional[int] = None
    template_id: Optional[int] = None

    @field_validator('code')
    @classmethod
    def validate_code(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        return validate_code_format(v)

class TaskResponse(TaskBase):
    id: int
    project_id: int
    asset_id: Optional[int] = None
    shot_id: Optional[int] = None
    category_id: Optional[int] = None
    domain_id: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

class TaskDeleteConfirm(BaseModel):
    password: str