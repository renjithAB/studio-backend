from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.task_template import TaskTemplate
from app.models.template import Template
from app.schemas.task_template import TaskTemplateCreate, TaskTemplateUpdate

class CRUDTaskTemplate:
    
    def get(self, db: Session, id: int) -> Optional[TaskTemplate]:
        return db.query(TaskTemplate).filter(
            TaskTemplate.id == id,
            TaskTemplate.is_active == True
        ).first()

    def get_by_code(self, db: Session, code: str) -> Optional[TaskTemplate]:
        return db.query(TaskTemplate).filter(
            TaskTemplate.code == code,
            TaskTemplate.is_active == True
        ).first()

    def get_multi(
        self, 
        db: Session, 
        skip: int = 0, 
        limit: int = 100,
        type: Optional[str] = None
    ) -> List[TaskTemplate]:
        query = db.query(TaskTemplate).filter(TaskTemplate.is_active == True)
        if type:
            query = query.filter(TaskTemplate.domain_code == type)
            
        return query.order_by(TaskTemplate.code).offset(skip).limit(limit).all()

    def create(
        self, 
        db: Session, 
        obj_in: TaskTemplateCreate,
        created_by: Optional[int] = None
    ) -> TaskTemplate:
        data = obj_in.model_dump(exclude_unset=True)
        applies_to_templates = data.pop("applies_to_templates", [])

        db_obj = TaskTemplate(
            **data,
            created_by=created_by,
            updated_by=created_by
        )
        db.add(db_obj)
        db.flush()

        if applies_to_templates:
            project_templates = db.query(Template).filter(Template.code.in_(applies_to_templates)).all()
            db_obj.project_templates = project_templates

        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(
        self, 
        db: Session, 
        db_obj: TaskTemplate,
        obj_in: TaskTemplateUpdate,
        updated_by: Optional[int] = None
    ) -> TaskTemplate:
        update_data = obj_in.model_dump(exclude_unset=True)
        applies_to_templates = update_data.pop("applies_to_templates", None)
        
        if updated_by:
            update_data["updated_by"] = updated_by
            
        for field, value in update_data.items():
            setattr(db_obj, field, value)
            
        if applies_to_templates is not None:
            project_templates = db.query(Template).filter(Template.code.in_(applies_to_templates)).all()
            db_obj.project_templates = project_templates
            
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def soft_delete(self, db: Session, id: int) -> Optional[TaskTemplate]:
        obj = self.get(db, id)
        if obj:
            obj.is_active = False
            db.commit()
        return obj

task_template = CRUDTaskTemplate()
