from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.auth.dependencies import get_current_user, get_db
from app.crud.crud_cycle import cycle as crud_cycle
from app.schemas.cycle import CycleCreate, CycleUpdate, CycleResponse
from app.models.users import User

router = APIRouter()

@router.post("/", response_model=CycleResponse, status_code=status.HTTP_201_CREATED)
def create_cycle(
    data: CycleCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new cycle entry"""
    return crud_cycle.create(db, obj_in=data)

@router.get("/{cycle_id}", response_model=CycleResponse)
def get_cycle(
    cycle_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific cycle by ID"""
    obj = crud_cycle.get(db, id=cycle_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Cycle not found")
    return obj

@router.put("/{cycle_id}", response_model=CycleResponse)
def update_cycle(
    cycle_id: int,
    data: CycleUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update a cycle entry"""
    obj = crud_cycle.get(db, id=cycle_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Cycle not found")
    return crud_cycle.update(db, db_obj=obj, obj_in=data)

@router.delete("/{cycle_id}")
def delete_cycle(
    cycle_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Soft delete a cycle entry"""
    obj = crud_cycle.soft_delete(db, id=cycle_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Cycle not found")
    return {"success": True, "id": cycle_id}
