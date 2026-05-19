# app/api/routes/assets.py
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user, get_db
from app.services.asset_service import asset_service
from app.schemas.asset import (
    AssetCreate, 
    AssetHierarchyOut, 
    AssetOut, 
    AssetUpdate
)
from app.schemas.asset import TaskWithVariants
from app.schemas.variant import VariantResponse
from app.crud.crud_asset import asset as crud_asset
from app.crud.crud_task import task as crud_task
from app.crud.crud_variant import variant as crud_variant
from app.models.users import User

router = APIRouter()

# Helper for ID validation
def validate_id(id_value: int) -> int:
    if id_value < 1000:
        raise HTTPException(
            status_code=400,
            detail=f"ID must be 1000 or greater, got {id_value}"
        )
    return id_value

@router.post("/", response_model=AssetOut, status_code=201)
def create_asset(
    data: AssetCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new asset under a category"""
    
    # Validate IDs
    validate_id(data.project_id)
    validate_id(data.category_id)
    
    try:
        asset = asset_service.create_asset(
            db=db,
            project_id=data.project_id,
            category_id=data.category_id,
            code=data.code,
            name=data.name,
            description=data.description,
            thumbnail_url=data.thumbnail_url,
            tag=data.tag,
            is_active=data.is_active,
            created_by=current_user.id,
            tasks=data.tasks
        )
        return asset
    except ValueError as e:
        raise HTTPException(status_code=409, detail=str(e))

@router.get("/", response_model=List[AssetOut])
def list_assets_root(
    project_id: Optional[int] = Query(None, description="Filter by project"),
    category_id: Optional[int] = Query(None, description="Filter by category"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List all assets with optional filtering"""
    return crud_asset.get_multi(
        db, project_id=project_id, category_id=category_id, skip=skip, limit=limit
    )

@router.get("/projects/{project_id}/assets", response_model=List[AssetOut])
def list_assets(
    project_id: int,
    category_id: Optional[int] = Query(None, description="Filter by category"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List all assets in a project, optionally filtered by category"""
    validate_id(project_id)
    
    if category_id:
        validate_id(category_id)
        return asset_service.get_assets_by_category(
            db, project_id=project_id, category_id=category_id, skip=skip, limit=limit
        )
    
    return crud_asset.get_multi(db, project_id=project_id, skip=skip, limit=limit)

@router.get("/{asset_id}", response_model=AssetOut)
def get_asset(
    asset_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific asset by ID"""
    validate_id(asset_id)
    
    asset = crud_asset.get(db, id=asset_id)
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")
    return asset

@router.put("/{asset_id}", response_model=AssetOut)
def update_asset(
    asset_id: int,
    data: AssetUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update an asset"""
    validate_id(asset_id)
    
    asset = crud_asset.get(db, id=asset_id)
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")
    
    return crud_asset.update(db, db_obj=asset, obj_in=data)

@router.get("/{asset_id}/hierarchy", response_model=AssetHierarchyOut)
def get_asset_hierarchy(
    asset_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get complete hierarchy for a specific asset (tasks + variants)"""
    validate_id(asset_id)
    
    asset = crud_asset.get(db, id=asset_id)
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")
        
    # Fetch tasks and variants
    from app.models.task import Task
    from app.models.variant import Variant
    from app.schemas.task import TaskResponse
    
    db_tasks = db.query(Task).filter(Task.asset_id == asset_id, Task.is_active == True).all()
    
    tasks_with_variants = []
    for t in db_tasks:
        variants = db.query(Variant).filter(Variant.task_id == t.id, Variant.is_active == True).all()
        tasks_with_variants.append(
            TaskWithVariants(
                **TaskResponse.model_validate(t).model_dump(),
                variants=[VariantResponse.model_validate(v) for v in variants]
            )
        )
        
    return AssetHierarchyOut(
        asset=AssetOut.model_validate(asset),
        tasks=tasks_with_variants
    )

@router.put("/{asset_id}", response_model=AssetOut)
def update_asset(
    asset_id: int,
    data: AssetUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update an asset"""
    validate_id(asset_id)
    
    asset = crud_asset.get(db, id=asset_id)
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")
    
    return crud_asset.update(db, db_obj=asset, obj_in=data, updated_by=current_user.id)

@router.delete("/{asset_id}")
def delete_asset(
    asset_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Soft delete an asset"""
    validate_id(asset_id)
    
    asset = crud_asset.soft_delete(db, id=asset_id)
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")
    
    return {"success": True, "id": asset_id}

# Get category templates for dropdown
@router.get("/categories", response_model=List[dict])
def get_asset_categories(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all asset category templates (Camera, Character, etc.)"""
    from app.models.template import Template
    
    categories = db.query(Template).filter(
        Template.tier == 'categoryTemplate',
        Template.domain == 'category',
        Template.is_active == True
    ).order_by(Template.code).all()
    
    return [
        {
            "id": c.id,
            "code": c.code.upper(),
            "name": c.name,
            "description": c.description
        }
        for c in categories
    ]