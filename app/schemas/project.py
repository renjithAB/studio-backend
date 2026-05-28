from pydantic import BaseModel, Field, validator
from app.core.validators import validate_code_format
from typing import Optional
from datetime import datetime

class ProjectBase(BaseModel):
    code: str
    name: Optional[str] = None
    # type: Optional[str] = None
    template_id: Optional[int] = Field(None, ge=1000, description="Template ID must be 1000 or greater")
    thumbnail_url: Optional[str] = None
    description: Optional[str] = None
    tag: Optional[str] = None
    
    @validator('template_id')
    def validate_template_id(cls, v):
        if v is not None and v < 1000:
            raise ValueError('Template ID must be 1000 or greater')
        return v

class ProjectCreate(ProjectBase):
    @validator('code')
    def validate_code(cls, v):
        return validate_code_format(v)

class ProjectUpdate(BaseModel):
    name: Optional[str] = None
    # type: Optional[str] = None
    template_id: Optional[int] = Field(None, ge=1000, description="Template ID must be 1000 or greater")
    thumbnail_url: Optional[str] = None
    description: Optional[str] = None
    tag: Optional[str] = None
    enable: Optional[bool] = None
    code: Optional[str] = None  # Allow updating code

    @validator('code')
    def validate_code(cls, v):
        if v is None:
            return v
        return validate_code_format(v)
    
    @validator('template_id')
    def validate_template_id(cls, v):
        if v is not None and v < 1000:
            raise ValueError('Template ID must be 1000 or greater')
        return v

class ProjectOut(ProjectBase):
    id: int = Field(..., ge=1000, description="Project ID must be 1000 or greater")
    is_active: bool
    template_name: Optional[str] = None
    created_at: Optional[datetime] = None
    created_by: Optional[int] = Field(None, ge=1000, description="Created by user ID must be 1000 or greater")
    updated_at: Optional[datetime] = None
    updated_by: Optional[int] = Field(None, ge=1000, description="Updated by user ID must be 1000 or greater")

    @validator('id')
    def validate_id(cls, v):
        if v < 1000:
            raise ValueError('Project ID must be 1000 or greater')
        return v
    
    @validator('created_by', 'updated_by')
    def validate_user_ids(cls, v):
        if v is not None and v < 1000:
            raise ValueError('User ID must be 1000 or greater')
        return v

    class Config:
        from_attributes = True