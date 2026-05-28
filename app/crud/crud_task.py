# app/crud/crud_task.py
from sqlalchemy.orm import Session
from app.models.task import Task
from app.schemas.task import TaskCreate, TaskUpdate
from app.crud.base import CRUDBase

class CRUDTask(CRUDBase[Task, TaskCreate, TaskUpdate]):
    def create_task(self, db: Session, task_in: TaskCreate) -> Task:
        return self.create(db, obj_in=task_in)

task = CRUDTask(Task)
