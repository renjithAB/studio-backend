from pydantic import BaseModel, ConfigDict, field_validator
from app.core.validators import validate_code_format
from typing import Optional
from datetime import datetime

class PublishTypeBase(BaseModel):
    project_id:        Optional[int] = None
    variant_id:        Optional[int] = None
    task_id:           Optional[int] = None
    name:              Optional[str] = None
    description:       Optional[str] = None
    is_active:         bool = True
    thumbnail_url:     Optional[str] = None
    code:              str
    publish_type_code: Optional[str] = None  # e.g. 'submit' or 'release'

    @field_validator('code')
    @classmethod
    def validate_code(cls, v: str) -> str:
        return validate_code_format(v)

class PublishTypeCreate(PublishTypeBase):
    pass

class PublishTypeUpdate(BaseModel):
    name:              Optional[str] = None
    description:       Optional[str] = None
    is_active:         Optional[bool] = None
    thumbnail_url:     Optional[str] = None
    publish_type_code: Optional[str] = None

class PublishTypeResponse(PublishTypeBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    created_by: Optional[int] = None
    updated_by: Optional[int] = None

    model_config = ConfigDict(from_attributes=True)
