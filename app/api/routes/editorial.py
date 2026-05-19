from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.auth.dependencies import get_current_user, get_db
from app.crud.crud_editorial import editorial as crud_editorial
from app.schemas.editorial import EditorialCreate, EditorialUpdate, EditorialResponse
from app.models.users import User

router = APIRouter()

@router.post("/", response_model=EditorialResponse, status_code=status.HTTP_201_CREATED)
def create_editorial(
    data: EditorialCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new editorial entry"""
    return crud_editorial.create(db, obj_in=data)

@router.get("/{editorial_id}", response_model=EditorialResponse)
def get_editorial(
    editorial_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific editorial by ID"""
    obj = crud_editorial.get(db, id=editorial_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Editorial not found")
    return obj

@router.put("/{editorial_id}", response_model=EditorialResponse)
def update_editorial(
    editorial_id: int,
    data: EditorialUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update an editorial entry"""
    obj = crud_editorial.get(db, id=editorial_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Editorial not found")
    return crud_editorial.update(db, db_obj=obj, obj_in=data)

@router.delete("/{editorial_id}")
def delete_editorial(
    editorial_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Soft delete an editorial entry"""
    obj = crud_editorial.soft_delete(db, id=editorial_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Editorial not found")
    return {"success": True, "id": editorial_id}
