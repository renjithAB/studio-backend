import os
import json

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user, get_db
from app.crud.crud_template import template as crud_template
from app.crud.crud_task_template import task_template as crud_task_template
from app.schemas.template import TemplateCreate, TemplateUpdate, TemplateOut
from app.models.users import User
from app.models.project import Project 
from app.models.template import Template
from app.schemas.task_template import TaskTemplateOut, TaskTemplateCreate, TaskTemplateUpdate

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
    res = crud_template.get_multi(db, skip=skip, limit=limit, tier=tier, domain=domain)
    
    merged_templates = []
    for t in res:
        merged_templates.append(t)
        
    # Query task templates and append them
    from app.models.task_template import TaskTemplate
    task_templates = db.query(TaskTemplate).filter(TaskTemplate.is_active == True).all()
    
    class TaskTemplateAdapter:
        def __init__(self, task_tmpl):
            self.id = task_tmpl.id
            self.code = task_tmpl.code
            self.name = task_tmpl.name
            self.description = task_tmpl.description
            self.thumbnail_url = None
            self.tag = "task"
            self.has_episode = False
            self.is_active = task_tmpl.is_active
            self.applicable_templates = ",".join(task_tmpl.applies_to_templates)
            self.created_at = task_tmpl.created_at
            self.updated_at = task_tmpl.updated_at
            self.created_by = task_tmpl.created_by
            self.updated_by = task_tmpl.updated_by

    for tt in task_templates:
        merged_templates.append(TaskTemplateAdapter(tt))
        
    # Query roles and append them
    from app.models.role import Role
    roles = db.query(Role).all()
    
    class RoleAdapter:
        def __init__(self, role):
            self.id = role.id
            self.code = role.code
            self.name = role.name
            self.description = role.description
            self.thumbnail_url = None
            self.tag = "role"
            self.has_episode = False
            self.is_active = role.is_active
            self.applicable_templates = None
            self.created_at = role.created_at
            self.updated_at = role.updated_at
            self.created_by = role.created_by
            self.updated_by = role.updated_by

    for r in roles:
        merged_templates.append(RoleAdapter(r))
        
    # Query permissions and append them
    from app.models.permission import Permission
    permissions = db.query(Permission).all()
    
    class PermissionAdapter:
        def __init__(self, perm):
            self.id = perm.id
            self.code = perm.code
            self.name = perm.name
            self.description = perm.description
            self.thumbnail_url = None
            self.tag = "permission"
            self.has_episode = False
            self.is_active = perm.is_active
            self.applicable_templates = None
            self.created_at = perm.created_at
            self.updated_at = perm.updated_at
            self.created_by = perm.created_by
            self.updated_by = perm.updated_by

    for p in permissions:
        merged_templates.append(PermissionAdapter(p))
        
    print(f"DEBUG: list_templates endpoint fetched {len(merged_templates)} merged templates from DB")
    return merged_templates

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
    from app.models.task_template import TaskTemplate
    
    query = db.query(TaskTemplate).filter(TaskTemplate.is_active == True)
    
    if type:
        query = query.filter(TaskTemplate.domain_code == type)
        
    if project_id:
        project_id = validate_id(project_id)
        
        # Fetch the project
        project = db.query(Project).filter(Project.id == project_id).first()
        if not project:
            raise HTTPException(status_code=404, detail=f"Project with ID {project_id} not found")
            
        # Fetch the template assigned to the project
        if project.template_id:
            query = query.filter(TaskTemplate.project_templates.any(Template.id == project.template_id))
        else:
            raise HTTPException(status_code=400, detail="Project does not have a template_id assigned")
            
    return query.all()

@router.post("/tasks", response_model=TaskTemplateOut, status_code=201)
def create_task_template(
    data: TaskTemplateCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new task template (admin only)"""
    if not current_user.is_super:
        raise HTTPException(status_code=403, detail="Only super users can create task templates")
    
    if crud_task_template.get_by_code(db, code=data.code):
        raise HTTPException(status_code=409, detail=f"Task template with code '{data.code}' already exists")
    
    return crud_task_template.create(db, obj_in=data, created_by=current_user.id)

@router.put("/tasks/{task_id}", response_model=TaskTemplateOut)
def update_task_template(
    task_id: int,
    data: TaskTemplateUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update a task template (admin only)"""
    if not current_user.is_super:
        raise HTTPException(status_code=403, detail="Only super users can update task templates")
    
    task_id = validate_id(task_id)
    db_task = crud_task_template.get(db, id=task_id)
    if not db_task:
        raise HTTPException(status_code=404, detail="Task template not found")
        
    return crud_task_template.update(db, db_obj=db_task, obj_in=data, updated_by=current_user.id)

@router.delete("/tasks/{task_id}")
def delete_task_template(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Soft delete a task template (admin only)"""
    if not current_user.is_super:
        raise HTTPException(status_code=403, detail="Only super users can delete task templates")
    
    task_id = validate_id(task_id)
    db_task = crud_task_template.get(db, id=task_id)
    if not db_task:
        raise HTTPException(status_code=404, detail="Task template not found")
        
    crud_task_template.soft_delete(db, id=task_id)
    return {"success": True, "id": task_id}

@router.get("/publish", response_model=List[TemplateOut])
def get_publish_templates(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all publish templates"""
    return crud_template.get_publish_templates(db)

@router.get("/publish-config")
def get_publish_config(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Return publish types from the templates table (tag='publish')."""
    publish_templates = (
        db.query(Template)
        .filter(Template.tag == "publish", Template.is_active == True)
        .order_by(Template.id)
        .all()
    )
    return [
        {"code": t.code, "name": t.name, "description": t.description}
        for t in publish_templates
    ]

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
    
    template = db.query(Template).filter(Template.id == template_id).first()
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
        
    # Prevent editing fields other than 'name' for default system templates
    DEFAULT_TEMPLATE_CODES = {
        "featurefilm", "youtube", "vfx", "shortfilm", "trailer", "game",
        "asset", "episode", "editorial", "library", "cycle"
    }
    if template.code in DEFAULT_TEMPLATE_CODES:
        update_fields = data.model_dump(exclude_unset=True)
        invalid_fields = [k for k in update_fields.keys() if k != "name"]
        if invalid_fields:
            raise HTTPException(
                status_code=400,
                detail=f"For default system templates, only the 'name' field is editable. Cannot edit: {', '.join(invalid_fields)}"
            )
    
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
    
    # Check if the template exists
    template = db.query(Template).filter(Template.id == template_id).first()
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
        
    # Prevent deleting default system templates
    DEFAULT_TEMPLATE_CODES = {
        "featurefilm", "youtube", "vfx", "shortfilm", "trailer", "game",
        "asset", "episode", "editorial", "library", "cycle"
    }
    if template.code in DEFAULT_TEMPLATE_CODES:
        raise HTTPException(
            status_code=400,
            detail="Default system templates cannot be deleted"
        )
    
    crud_template.soft_delete(db, id=template_id)
    return {"success": True, "id": template_id}