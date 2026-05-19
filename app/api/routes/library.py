from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.auth.dependencies import get_current_user, get_db
from app.crud.crud_library import library as crud_library
from app.schemas.library import LibraryCreate, LibraryUpdate, LibraryResponse
from app.models.users import User

router = APIRouter()

@router.post("/", response_model=LibraryResponse, status_code=status.HTTP_201_CREATED)
def create_library(
    data: LibraryCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new library entry"""
    return crud_library.create(db, obj_in=data)

@router.get("/{library_id}", response_model=LibraryResponse)
def get_library(
    library_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific library by ID"""
    obj = crud_library.get(db, id=library_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Library not found")
    return obj

@router.put("/{library_id}", response_model=LibraryResponse)
def update_library(
    library_id: int,
    data: LibraryUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update a library entry"""
    obj = crud_library.get(db, id=library_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Library not found")
    return crud_library.update(db, db_obj=obj, obj_in=data)

@router.delete("/{library_id}")
def delete_library(
    library_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Soft delete a library entry"""
    obj = crud_library.soft_delete(db, id=library_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Library not found")
    return {"success": True, "id": library_id}
