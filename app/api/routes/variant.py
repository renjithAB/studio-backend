from typing import List, Optional
from fastapi import APIRouter, Depends, status, HTTPException, Query
from sqlalchemy.orm import Session
from app.auth.dependencies import get_current_user, get_db
from app.schemas.variant import VariantCreate, VariantUpdate, VariantResponse
from app.crud.crud_variant import variant as variant_crud
from app.models.variant import Variant
from app.models.users import User

router = APIRouter()

@router.post("/", response_model=List[VariantResponse], status_code=status.HTTP_201_CREATED)
def create_variant(
    *,
    db: Session = Depends(get_db),
    variant_in: VariantCreate,
):
    """
    Create a new variant under a task, or optionally under all tasks of the asset.
    """
    from app.models.task import Task
    
    if variant_in.create_for_all_tasks:
        # Get all active tasks for the asset
        tasks = db.query(Task).filter(Task.asset_id == variant_in.asset_id, Task.is_active == True).all()
        created_variants = []
        
        for t in tasks:
            # Check if variant already exists for this task
            exists = db.query(Variant).filter(
                Variant.task_id == t.id,
                Variant.code == variant_in.code,
                Variant.is_active == True
            ).first()
            if not exists:
                db_obj = Variant(
                    **variant_in.model_dump(exclude={"create_for_all_tasks", "task_id"}),
                    task_id=t.id
                )
                db.add(db_obj)
                created_variants.append(db_obj)
                
        db.commit()
        for v in created_variants:
            db.refresh(v)
        return created_variants
    else:
        created = variant_crud.create(db=db, obj_in=variant_in)
        return [created]

@router.get("/tasks/{task_id}/variants", response_model=List[VariantResponse])
def get_task_variants(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Retrieve all variants for a specific task"""
    return db.query(Variant).filter(Variant.task_id == task_id, Variant.is_active == True).all()

@router.get("/assets/{asset_id}/variants", response_model=List[VariantResponse])
def get_asset_variants(
    asset_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Retrieve all variants check for a specific asset"""
    return db.query(Variant).filter(Variant.asset_id == asset_id, Variant.is_active == True).all()

@router.put("/{variant_id}", response_model=VariantResponse)
def update_variant(
    variant_id: int,
    data: VariantUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update a variant"""
    obj = variant_crud.get(db, id=variant_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Variant not found")
    return variant_crud.update(db, db_obj=obj, obj_in=data)