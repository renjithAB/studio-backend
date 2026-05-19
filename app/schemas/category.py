# app/schemas/category.py

from pydantic import BaseModel, ConfigDict, Field, field_validator
from app.core.validators import validate_code_format
from typing import Optional, List
from datetime import datetime

class CategoryBase(BaseModel):
    code: str
    name: str
    description: Optional[str] = None
    project_id: int 
    domain_id: int
    is_active: bool = True
    thumbnail_url: Optional[str] = None

class CategoryCreate(CategoryBase):
    tier: str = "categoryTemplate"

    @field_validator('code')
    @classmethod
    def validate_code(cls, v: str) -> str:
        return validate_code_format(v)

class CategoryUpdate(BaseModel):
    """Schema for updating a category - all fields optional"""
    name: Optional[str] = Field(None, description="Category name")
    description: Optional[str] = Field(None, description="Category description")
    project_id: Optional[int] = Field(None, description="Project ID this category belongs to")
    is_active: Optional[bool] = Field(None, description="Whether the category is active")
    code: Optional[str] = Field(None, description="Category code")
    thumbnail_url: Optional[str] = Field(None, description="Category thumbnail URL")

    @field_validator('code')
    @classmethod
    def validate_code(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        return validate_code_format(v)
    
    class Config:
        json_schema_extra = {
            "example": {
                "name": "Camera Equipment",
                "description": "All camera-related assets",
                "project_id": 2009,
                "is_active": True
            }
        }

class Category_response(CategoryBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    created_by: Optional[int] = None
    updated_by: Optional[int] = None
    project_id: int
    domain_id: int

    model_config = ConfigDict(from_attributes=True)