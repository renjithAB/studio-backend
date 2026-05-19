from typing import List, Optional
from fastapi import APIRouter, Depends, status, HTTPException, Query
from sqlalchemy.orm import Session
from app.auth.dependencies import get_current_user, get_db
from app.schemas.task import TaskCreate, TaskResponse, TaskUpdate, TaskDeleteConfirm
from app.crud.crud_task import task as task_crud
from app.models.task import Task
from app.models.users import User
from app.core.security import verify_password

router = APIRouter()

@router.post("/", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
def create_task(
    *,
    db: Session = Depends(get_db),
    task_in: TaskCreate,
):
    """
    Create a new task under an asset.
    """
    task = task_crud.create(db=db, obj_in=task_in)
    return task

@router.get("/assets/{asset_id}/tasks", response_model=List[TaskResponse])
def get_asset_tasks(
    asset_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Retrieve all tasks for a specific asset"""
    return db.query(Task).filter(Task.asset_id == asset_id, Task.is_active == True).all()

@router.get("/shots/{shot_id}/tasks", response_model=List[TaskResponse])
def get_shot_tasks(
    shot_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Retrieve all tasks for a specific shot"""
    return db.query(Task).filter(Task.shot_id == shot_id, Task.is_active == True).all()

@router.put("/{task_id}", response_model=TaskResponse)
def update_task(
    task_id: int,
    data: TaskUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update a task"""
    obj = task_crud.get(db, id=task_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Task not found")
    return task_crud.update(db, db_obj=obj, obj_in=data)

@router.delete("/{task_id}")
def delete_task(
    task_id: int,
    data: TaskDeleteConfirm,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Securely delete a task and all its sub-entities (variants/versions) after password verification"""
    # 1. Verify password
    if not verify_password(data.password, current_user.private_key):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid confirmation password"
        )
    
    # 2. Check if task exists
    obj = task_crud.get(db, id=task_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Task not found")
    
    # 3. Cascading delete (handled by DB due to ondelete="CASCADE" added earlier)
    task_crud.remove(db, id=task_id)
    
    return {"success": True, "message": "Task and sub-entities deleted successfully"}