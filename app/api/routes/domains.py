from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.auth.dependencies import get_current_user, get_db
from app.crud.crud_domain import domain as crud_domain
from app.schemas.domain import DomainCreate, DomainUpdate, DomainResponse
from app.models.users import User

router = APIRouter()

@router.get("/", response_model=List[DomainResponse])
def list_domains(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List all domains for a project"""
    return crud_domain.get_by_project(db, project_id=project_id)

@router.get("/{domain_id}", response_model=DomainResponse)
def get_domain(
    domain_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific domain by ID"""
    obj = crud_domain.get(db, id=domain_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Domain not found")
    return obj

@router.put("/{domain_id}", response_model=DomainResponse)
def update_domain(
    domain_id: int,
    data: DomainUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update a domain"""
    obj = crud_domain.get(db, id=domain_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Domain not found")
    return crud_domain.update(db, db_obj=obj, obj_in=data)

@router.delete("/{domain_id}")
def delete_domain(
    domain_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Soft delete a domain"""
    obj = crud_domain.soft_delete(db, id=domain_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Domain not found")
    return {"success": True, "id": domain_id}
