from pydantic import BaseModel, ConfigDict, Field, validator
from app.core.validators import validate_code_format
from typing import List, Optional
from datetime import datetime
from app.schemas.task import TaskResponse
from app.schemas.variant import VariantResponse

class AssetBase(BaseModel):
    code: str
    name: str
    description: Optional[str] = None
    thumbnail_url: Optional[str] = None
    tag: Optional[str] = None
    is_active: bool = True
    tasks: Optional[List[str]] = []

class AssetCreate(AssetBase):
    project_id: int = Field(..., ge=1000)
    category_id: int = Field(..., ge=1000)  # Camera, Character, etc. template ID
    domain_id: Optional[int] = Field(None, ge=1000)
    template_id: Optional[int] = Field(None, ge=1000)
    
    @validator('code')
    def validate_code(cls, v):
        return validate_code_format(v)

class AssetUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    thumbnail_url: Optional[str] = None
    tag: Optional[str] = None
    is_active: Optional[bool] = None
    code: Optional[str] = None

    @validator('code')
    def validate_code(cls, v):
        if v is None:
            return v
        return validate_code_format(v)

class AssetOut(AssetBase):
    id: int
    project_id: int
    category_id: int
    template_id: Optional[int]
    created_at: datetime
    updated_at: Optional[datetime]
    created_by: Optional[int]
    updated_by: Optional[int]
    
    class Config:
        from_attributes = True

class TaskWithVariants(TaskResponse):
    variants: List[VariantResponse] = []

class AssetHierarchyOut(BaseModel):
    asset: AssetOut
    tasks: List[TaskWithVariants] = []