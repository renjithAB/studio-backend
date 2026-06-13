from pydantic import BaseModel, ConfigDict, field_validator
from app.core.validators import validate_code_format
from typing import Optional
from datetime import datetime


class VersionBase(BaseModel):
    code: str
    name: str
    version_number: str = "v001"
    project_id: int
    publish_id: Optional[int] = None   # publish_types.id
    asset_id: Optional[int] = None
    category_id: Optional[int] = None
    variant_id: Optional[int] = None
    task_id: Optional[int] = None
    episode_id: Optional[int] = None
    sequence_id: Optional[int] = None
    shot_id: Optional[int] = None
    library_id: Optional[int] = None
    cycle_id: Optional[int] = None
    editorial_id: Optional[int] = None
    description: Optional[str] = None
    tag: Optional[str] = None
    thumbnail_url: Optional[str] = None
    movie_url: Optional[str] = None
    image_path: Optional[str] = None
    video_path: Optional[str] = None
    is_active: bool = True

    @field_validator("code")
    @classmethod
    def validate_code(cls, v: str) -> str:
        return validate_code_format(v)


class VersionCreate(VersionBase):
    pass


class VersionUpdate(BaseModel):
    name: Optional[str] = None
    version_number: Optional[str] = None
    description: Optional[str] = None
    tag: Optional[str] = None
    thumbnail_url: Optional[str] = None
    movie_url: Optional[str] = None
    image_path: Optional[str] = None
    video_path: Optional[str] = None
    is_active: Optional[bool] = None


class VersionResponse(VersionBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    created_by: Optional[int] = None
    updated_by: Optional[int] = None

    model_config = ConfigDict(from_attributes=True)
