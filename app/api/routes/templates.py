import os
import json

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user, get_db
from app.crud.crud_template import template as crud_template
from app.schemas.template import TemplateCreate, TemplateUpdate, TemplateOut
from app.models.users import User
from app.models.project import Project 
from app.models.template import Template
from app.schemas.template import TaskTemplateOut

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

@router.get("/", response_model=List[TemplateOut])
def list_templates(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    tier: Optional[str] = Query(None, description="Filter by tier (projectTemplate, domainTemplate, etc.)"),
    domain: Optional[str] = Query(None, description="Filter by domain"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all templates with optional filters"""
    return crud_template.get_multi(db, skip=skip, limit=limit, tier=tier, domain=domain)

@router.get("/domains/project/{project_id}", response_model=List[TemplateOut])
def get_domain_templates_for_project(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all domain templates that apply to a specific project"""
    # Validate project_id
    project_id = validate_id(project_id)
    
    return crud_template.get_domain_templates_for_project(db, project_id)

@router.get("/categories", response_model=List[TemplateOut])
def get_category_templates(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all category templates"""
    return crud_template.get_category_templates(db)

@router.get("/tasks", response_model=List[TaskTemplateOut])
def get_task_templates(
    type: Optional[str] = Query(None, description="Domain type (e.g., asset, shot, editorial)"),
    project_id: Optional[int] = Query(None, description="Project ID to filter applicable templates"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get task templates filtered by domain type and the project's base template.
    """
    # 1. Resolve the Project Template Code (if project_id is provided)
    project_template_code = None
    
    if project_id:
        project_id = validate_id(project_id)
        
        # Fetch the project
        project = db.query(Project).filter(Project.id == project_id).first()
        if not project:
            raise HTTPException(status_code=404, detail=f"Project with ID {project_id} not found")
            
        # Fetch the template assigned to the project
        if project.template_id:
            template = db.query(Template).filter(Template.id == project.template_id).first()
            if template:
                project_template_code = template.code
            else:
                raise HTTPException(status_code=404, detail="Assigned project template not found in DB")
        else:
            raise HTTPException(status_code=400, detail="Project does not have a template_id assigned")

    # 2. Load the JSON configuration
    # Ensure this path matches the location relative to where you run your FastAPI app
    config_path = os.path.join("app/core", "template_config.json")
    
    try:
        with open(config_path, "r") as f:
            config_data = json.load(f)
    except FileNotFoundError:
        raise HTTPException(status_code=500, detail="template_config.json file not found")
    except json.JSONDecodeError:
        raise HTTPException(status_code=500, detail="Error decoding template_config.json")

    all_tasks = config_data.get("tasks", [])
    filtered_tasks = []

    # 3. Filter the tasks
    for task in all_tasks:
        # Filter by domain_code (mapped from the 'type' query param)
        if type and task.get("domain_code") != type:
            continue
            
        # Filter by project template code
        if project_template_code:
            applies_to = task.get("applies_to_templates", [])
            if project_template_code not in applies_to:
                continue
                
        filtered_tasks.append(task)

    return filtered_tasks

@router.get("/publish", response_model=List[TemplateOut])
def get_publish_templates(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all publish templates"""
    return crud_template.get_publish_templates(db)

@router.get("/publish-config")
def get_publish_config_from_file(
    current_user: User = Depends(get_current_user)
):
    """Return publish types defined in template_config.json (no DB needed)."""
    config_path = os.path.join("app/core", "template_config.json")
    try:
        with open(config_path, "r") as f:
            config_data = json.load(f)
    except FileNotFoundError:
        raise HTTPException(status_code=500, detail="template_config.json not found")
    except json.JSONDecodeError:
        raise HTTPException(status_code=500, detail="Error decoding template_config.json")
    return config_data.get("publish", [])

@router.get("/{template_id}", response_model=TemplateOut)
def get_template(
    template_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific template by ID"""
    # Validate template_id
    template_id = validate_id(template_id)
    
    template = crud_template.get(db, id=template_id)
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    return template

@router.get("/code/{code}", response_model=TemplateOut)
def get_template_by_code(
    code: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific template by code"""
    template = crud_template.get_by_code(db, code=code)
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    return template

@router.post("/", response_model=TemplateOut, status_code=201)
def create_template(
    data: TemplateCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new template (admin only)"""
    if not current_user.is_super:
        raise HTTPException(status_code=403, detail="Only super users can create templates")
    
    if crud_template.get_by_code(db, code=data.code):
        raise HTTPException(status_code=409, detail=f"Template with code '{data.code}' already exists")
    
    return crud_template.create(db, obj_in=data, created_by=current_user.id)

@router.put("/{template_id}", response_model=TemplateOut)
def update_template(
    template_id: int,
    data: TemplateUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update a template (admin only)"""
    if not current_user.is_super:
        raise HTTPException(status_code=403, detail="Only super users can update templates")
    
    # Validate template_id
    template_id = validate_id(template_id)
    
    template = crud_template.get(db, id=template_id)
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    
    return crud_template.update(db, db_obj=template, obj_in=data, updated_by=current_user.id)

@router.delete("/{template_id}")
def delete_template(
    template_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Soft delete a template (admin only)"""
    if not current_user.is_super:
        raise HTTPException(status_code=403, detail="Only super users can delete templates")
    
    # Validate template_id
    template_id = validate_id(template_id)
    
    template = crud_template.soft_delete(db, id=template_id)
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    
    return {"success": True, "id": template_id}