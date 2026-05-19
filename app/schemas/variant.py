from typing import Optional
from pydantic import BaseModel, ConfigDict
from datetime import datetime
from app.models.variant import PriorityEnum, StatusEnum


class VariantBase(BaseModel):
    code: str
    name: str
    description: Optional[str] = None
    tag: Optional[str] = None
    is_active: bool = True
    thumbnail_url: Optional[str] = None
    # Pipeline tracking fields
    man_days:    Optional[float] = None
    start_at:    Optional[datetime] = None
    end_at:      Optional[datetime] = None
    priority:    Optional[PriorityEnum] = None
    assigned_by: Optional[int] = None
    review_by:   Optional[int] = None
    status:      Optional[StatusEnum] = None


class VariantCreate(VariantBase):
    project_id: int
    asset_id: int
    task_id: Optional[int] = None
    create_for_all_tasks: bool = False


class VariantUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    tag: Optional[str] = None
    is_active: Optional[bool] = None
    thumbnail_url: Optional[str] = None
    # Pipeline tracking fields
    man_days:    Optional[float] = None
    start_at:    Optional[datetime] = None
    end_at:      Optional[datetime] = None
    priority:    Optional[PriorityEnum] = None
    assigned_by: Optional[int] = None
    review_by:   Optional[int] = None
    status:      Optional[StatusEnum] = None


class VariantResponse(VariantBase):
    id: int
    project_id: int
    asset_id: int
    task_id: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)