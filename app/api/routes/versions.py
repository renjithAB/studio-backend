from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.schemas.version import VersionCreate, VersionUpdate, VersionResponse
from app.crud.crud_version import version as crud_version
from app.auth.dependencies import get_current_user, get_db
from app.models.users import User

router = APIRouter()

@router.post("/", response_model=VersionResponse, status_code=status.HTTP_201_CREATED)
def create_version(
    *,
    db: Session = Depends(get_db),
    version_in: VersionCreate,
    current_user: User = Depends(get_current_user)
):
    """
    Create a new version under a publish type.
    """
    # Verify the code is format-validated or handle custom logic if needed
    return crud_version.create(
        db=db,
        obj_in=version_in,
        created_by=current_user.id if current_user else None
    )

@router.get("/{version_id}", response_model=VersionResponse)
def get_version(
    version_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a version by ID"""
    obj = crud_version.get(db, id=version_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Version not found")
    return obj

@router.put("/{version_id}", response_model=VersionResponse)
def update_version(
    version_id: int,
    data: VersionUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update a version"""
    obj = crud_version.get(db, id=version_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Version not found")
    return crud_version.update(
        db, 
        db_obj=obj, 
        obj_in=data, 
        updated_by=current_user.id if current_user else None
    )
