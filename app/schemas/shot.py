from pydantic import BaseModel, ConfigDict, Field, field_validator
from app.core.validators import validate_code_format
from typing import Optional, List
from datetime import datetime

class ShotBase(BaseModel):
    code: str
    name: str
    description: Optional[str] = None
    project_id: int
    sequence_id: int
    is_active: bool = True
    thumbnail_url: Optional[str] = None
    frame_start: Optional[int] = None
    frame_end: Optional[int] = None

class ShotCreate(ShotBase):
    @field_validator('code')
    @classmethod
    def validate_code(cls, v: str) -> str:
        return validate_code_format(v)
    
    tasks: Optional[List[str]] = Field(None, description="Initial tasks to create for this shot")

class ShotUpdate(BaseModel):
    code: Optional[str] = None
    name: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None
    thumbnail_url: Optional[str] = None

    @field_validator('code')
    @classmethod
    def validate_code(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        return validate_code_format(v)

class ShotResponse(ShotBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    created_by: Optional[int] = None
    updated_by: Optional[int] = None

    model_config = ConfigDict(from_attributes=True)