from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.services.publish_type_service import PublishTypeService
from app.schemas.publish_types import PublishTypeCreate, PublishTypeUpdate, PublishTypeResponse
from app.crud.crud_publish_type import publish_type as crud_publish_type
from app.auth.dependencies import get_current_user, get_db
from app.models.users import User  # adjust import

router = APIRouter()
service = PublishTypeService()

@router.post("/", response_model=PublishTypeResponse, status_code=status.HTTP_201_CREATED)
def create_publish_type(
    *,
    db: Session = Depends(get_db),
    publish_type_in: PublishTypeCreate,
    current_user: User = Depends(get_current_user)  # if you have authentication
):
    """
    Create a new publish type.
    
    - **code**: unique identifier for the publish type
    - **name**: display name
    - **project_id**: ID of the project this belongs to
    - **is_active**: (optional) whether the publish type is active, defaults to true
    - **description**: (optional) additional details
    """
    # Optionally, you can add validation here (e.g., check if code already exists)
    # existing = db.query(PublishType).filter(PublishType.code == publish_type_in.code).first()
    # if existing:
    #     raise HTTPException(status_code=400, detail="Publish type with this code already exists")
    
    return service.create_publish_type(
        db=db,
        publish_type_in=publish_type_in,
        created_by=current_user.id if current_user else None
    )

@router.put("/{publish_type_id}", response_model=PublishTypeResponse)
def update_publish_type(
    publish_type_id: int,
    data: PublishTypeUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update a publish type"""
    obj = crud_publish_type.get(db, id=publish_type_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Publish type not found")
    return crud_publish_type.update(db, db_obj=obj, obj_in=data)