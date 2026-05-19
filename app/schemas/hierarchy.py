from typing import List, Optional, Union,Dict, Any
from pydantic import BaseModel, Field, validator
from app.core.validators import validate_code_format

# Base Entity Schema
class HierarchyEntity(BaseModel):
    id: Optional[int] = Field(None, description="ID for real entities, null for headers")
    type: str
    domain_type: Optional[str] = None 
    code: str
    name: str
    thumbnail_url: Optional[str] = None
    description: Optional[str] = None
    children: List['HierarchyEntity'] = []
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)

    class Config:
        from_attributes = True
# Project Hierarchy
class ProjectHierarchy(HierarchyEntity):
    type: str = 'project'
    template_code: Optional[str] = None
    template_name: Optional[str] = None
    episode_count: int = 0
    asset_count: int = 0
    sequence_count: int = 0
    shot_count: int = 0
    editorial_count: int = 0
    library_count: int = 0
    cycle_count: int = 0
    variant_count: int = 0
    task_count:int =0

# Episode Hierarchy
class EpisodeHierarchy(HierarchyEntity):
    type: str = 'episode'
    sequence_count: Optional[int] = None
    shot_count: Optional[int] = None

# Sequence Hierarchy
class SequenceHierarchy(HierarchyEntity):
    type: str = 'sequence'
    frame_start: Optional[int] = None
    frame_end: Optional[int] = None
    shot_count: Optional[int] = None

# Shot Hierarchy
class ShotHierarchy(HierarchyEntity):
    type: str = 'shot'
    frame_start: Optional[int] = None
    frame_end: Optional[int] = None
    cut_in: Optional[int] = None
    cut_out: Optional[int] = None
    asset_count: Optional[int] = None

# Asset Hierarchy
class AssetHierarchy(HierarchyEntity):
    type: str = 'asset'
    category_code: Optional[str] = None
    category_name: Optional[str] = None
    variant_count: Optional[int] = None

# Variant Hierarchy
class VariantHierarchy(HierarchyEntity):
    type: str = 'variant'
    asset_id: int = Field(..., ge=1000)

    @validator('asset_id')
    def validate_asset_id(cls, v):
        if v < 1000:
            raise ValueError('Asset ID must be 1000 or greater')
        return v

# Editorial Hierarchy
class EditorialHierarchy(HierarchyEntity):
    type: str = 'editorial'
    episode_id: Optional[int] = Field(None, ge=1000)

    @validator('episode_id')
    def validate_episode_id(cls, v):
        if v is not None and v < 1000:
            raise ValueError('Episode ID must be 1000 or greater')
        return v

# Library Hierarchy
class LibraryHierarchy(HierarchyEntity):
    type: str = 'library'
    cycle_count: Optional[int] = None

# Cycle Hierarchy
class CycleHierarchy(HierarchyEntity):
    type: str = 'cycle'
    library_id: int = Field(..., ge=1000)

    @validator('library_id')
    def validate_library_id(cls, v):
        if v < 1000:
            raise ValueError('Library ID must be 1000 or greater')
        return v

# Project Summary
class ProjectSummary(BaseModel):
    project_id: int = Field(..., ge=1000)
    counts: dict

    @validator('project_id')
    def validate_project_id(cls, v):
        if v < 1000:
            raise ValueError('Project ID must be 1000 or greater')
        return v

    class Config:
        from_attributes = True

# For the children endpoint, we can just return a list of HierarchyEntity
# since the frontend can determine the type from the 'type' field

# Update forward references
HierarchyEntity.update_forward_refs()