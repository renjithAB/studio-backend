from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.auth.dependencies import get_current_user, get_db
from app.services.hierarchy_service import hierarchy_service
from app.schemas.hierarchy import ProjectHierarchy, HierarchyEntity, ProjectSummary
from app.models.users import User
from app.models.episode import Episode
from app.models.sequence import Sequence
from app.models.shot import Shot
from app.models.asset import Asset
from app.models.editorial import Editorial
from app.models.library import Library

router = APIRouter()

# Helper function for ID validation
def validate_id(id_value: int) -> int:
    """Validate that ID is an integer and >= 1000"""
    if not isinstance(id_value, int):
        try:
            id_value = int(id_value)
        except (ValueError, TypeError):
            raise HTTPException(
                status_code=400, 
                detail=f"ID must be an integer, got {type(id_value).__name__}"
            )
    
    if id_value < 1000:
        raise HTTPException(
            status_code=400, 
            detail=f"ID must be 1000 or greater, got {id_value}"
        )
    
    return id_value

@router.get("/project/{project_id}", response_model=ProjectHierarchy)
def get_project_hierarchy(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get complete hierarchical view of a project"""
    # Validate project_id
    project_id = validate_id(project_id)
    
    hierarchy = hierarchy_service.get_project_hierarchy(db, project_id)
    if not hierarchy:
        raise HTTPException(status_code=404, detail="Project not found")
    return hierarchy

@router.get("/{project_id}/{entity_type}/{entity_id}/children", response_model=List[HierarchyEntity])
def get_entity_children(
    project_id: int,
    entity_type: str,
    entity_id: int,
    domain_type: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get direct children of any entity (for lazy loading)"""
    valid_types = [
        "project", "episode", "sequence", "shot", "asset", 
        "library", "editorial", "category", "task", "variant", "cycle", "domain", "publish", "version"
    ]
    
    if entity_type not in valid_types:
        raise HTTPException(
            status_code=400, 
            detail=f"Invalid entity type. Must be one of: {valid_types}"
        )
    
    # Validate entity_id unless it is a virtual domain with negative ID
    if not (entity_type == "domain" and entity_id < 0):
        entity_id = validate_id(entity_id)
    
    # Call the new service method
    children = hierarchy_service.get_entity_children(db, project_id, entity_type, entity_id, domain_type=domain_type)
    
    return children

@router.get("/project/{project_id}/summary", response_model=ProjectSummary)
def get_project_summary(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get summary counts for a project"""
    # Validate project_id
    project_id = validate_id(project_id)
    
    counts = {
        "episodes": db.query(func.count(Episode.id)).filter(
            Episode.project_id == project_id,
            Episode.is_active == True
        ).scalar() or 0,
        
        "sequences": db.query(func.count(Sequence.id)).filter(
            Sequence.project_id == project_id,
            Sequence.is_active == True
        ).scalar() or 0,
        
        "shots": db.query(func.count(Shot.id)).filter(
            Shot.project_id == project_id,
            Shot.is_active == True
        ).scalar() or 0,
        
        "assets": db.query(func.count(Asset.id)).filter(
            Asset.project_id == project_id,
            Asset.is_active == True
        ).scalar() or 0,
        
        "editorials": db.query(func.count(Editorial.id)).filter(
            Editorial.project_id == project_id,
            Editorial.is_active == True
        ).scalar() or 0,
        
        "libraries": db.query(func.count(Library.id)).filter(
            Library.project_id == project_id,
            Library.is_active == True
        ).scalar() or 0,
    }
    
    return ProjectSummary(project_id=project_id, counts=counts)