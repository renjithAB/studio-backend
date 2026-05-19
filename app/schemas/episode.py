from pydantic import BaseModel, ConfigDict, Field, field_validator
from app.core.validators import validate_code_format
from typing import Optional
from datetime import datetime

class EpisodeBase(BaseModel):
    code: str
    name: str
    description: Optional[str] = None
    project_id: int
    is_active: bool = True
    domain_id:int
    thumbnail_url: Optional[str] = None
    

class EpisodeCreate(EpisodeBase):
    create_extra_nodes: bool

    @field_validator('code')
    @classmethod
    def validate_code(cls, v: str) -> str:
        return validate_code_format(v)

class EpisodeUpdate(BaseModel):
    code: Optional[str] = Field(None, description="Episode code")
    name: Optional[str] = Field(None, description="Episode name")
    description: Optional[str] = Field(None, description="Episode description")
    is_active: Optional[bool] = Field(None, description="Active status")
    thumbnail_url: Optional[str] = Field(None, description="Thumbnail URL")

    @field_validator('code')
    @classmethod
    def validate_code(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        return validate_code_format(v)

class EpisodeResponse(EpisodeBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    created_by: Optional[int] = None
    updated_by: Optional[int] = None

    model_config = ConfigDict(from_attributes=True)  # ORM mode