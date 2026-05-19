from fastapi import APIRouter, Depends, HTTPException, Query,  UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import List, Optional

from app.auth.dependencies import get_current_user, get_db
from app.crud.crud_project import project as crud_project
from app.schemas.project import ProjectCreate, ProjectUpdate, ProjectOut
from app.services.ProjectService import ProjectService
from app.models.users import User

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

@router.get("/", response_model=List[ProjectOut])
def list_projects(
    skip: int = 0,
    limit: int = 100,
    type: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return crud_project.get_multi(db, skip=skip, limit=limit, type=type)

@router.get("/{project_id}", response_model=ProjectOut)
def get_project(
    project_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    # Validate project_id
    project_id = validate_id(project_id)
    
    obj = crud_project.get(db, id=project_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Project not found")
    return obj

@router.post("/")
async def create_project(
    *,
    db: Session = Depends(get_db),
    code: str = Form(...),
    name: str = Form(...),
    description: Optional[str] = Form(None),
    template_id: Optional[int] = Form(None),
    thumbnail: Optional[UploadFile] = File(None),
    current_user: User = Depends(get_current_user)
):
    """Create a new project with optional thumbnail"""
    
    existing_project = crud_project.get_by_code(db, code=code)
    if existing_project:
        raise HTTPException(status_code=400, detail="Project with this code already exists")

    
    project_data = ProjectCreate(
        code=code,
        name=name,
        description=description,
        template_id=template_id
    )
    
    project = await ProjectService.create_project_with_default_structure(
        db=db,
        project_data=project_data,
        created_by=current_user.id,
        thumbnail_file=thumbnail
    )
    
    return project

@router.put("/{project_id}", response_model=ProjectOut)
def update_project(
    project_id: int,
    data: ProjectUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    # Validate project_id
    project_id = validate_id(project_id)
    
    obj = crud_project.get(db, id=project_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Project not found")
    if data.code if hasattr(data, 'code') else False:
        pass  # code not updatable
    return crud_project.update(db, db_obj=obj, obj_in=data, updated_by=current_user.id)

@router.delete("/{project_id}")
def delete_project(
    project_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    # Validate project_id
    project_id = validate_id(project_id)
    
    obj = crud_project.soft_delete(db, id=project_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Project not found")
    return {"success": True, "id": project_id}