# app/crud/crud_task.py
from sqlalchemy.orm import Session
from app.models.task import Task
from app.schemas.task import TaskCreate

class CRUDTask:
    def create_task(self, db: Session, task_in: TaskCreate) -> Task:
        db_obj = Task(
            code=task_in.code,
            name=task_in.name,
            project_id=task_in.project_id,
            asset_id=task_in.asset_id,
            is_active=task_in.is_active
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def get_multi(self, db: Session, *, skip: int = 0, limit: int = 100):
        return db.query(Task).offset(skip).limit(limit).all()

task = CRUDTask()
