from typing import List, Optional, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_
from app.models.template import Template
from app.schemas.template import TemplateCreate, TemplateUpdate

class CRUDTemplate:
    
    def get(self, db: Session, id: int) -> Optional[Template]:
        return db.query(Template).filter(
            Template.id == id,
            Template.is_active == True
        ).first()

    def get_by_code(self, db: Session, code: str) -> Optional[Template]:
        return db.query(Template).filter(
            Template.code == code,
            Template.is_active == True
        ).first()

    def get_multi(
        self, 
        db: Session, 
        skip: int = 0, 
        limit: int = 100,
        tier: Optional[str] = None,
        domain: Optional[str] = None
    ) -> List[Template]:
        query = db.query(Template).filter(
            Template.is_active == True,
            (Template.tag.is_(None)) | (~Template.tag.in_(['role', 'permission']))
        )
            
        return query.order_by(Template.code).offset(skip).limit(limit).all()

    def get_domain_templates_for_project(
        self, 
        db: Session, 
        project_id: int
    ) -> List[Template]:
        """Get all domain templates that apply to a specific project"""
        from app.models.project import Project
        project = db.query(Project).filter(Project.id == project_id).first()
        if not project or not project.template_id:
            return []
        
        project_template = db.query(Template).filter(
            Template.id == project.template_id,
            Template.is_active == True
        ).first()
        if not project_template:
            return []
        return project_template.domain_templates

    def get_category_templates(self, db: Session) -> List[Template]:
        """Get all category templates"""
        return db.query(Template).filter(
            Template.tag == 'category',
            Template.is_active == True
        ).all()

    def get_task_templates(self, db: Session) -> List[Template]:
        """Get all task templates"""
        return db.query(Template).filter(
            Template.tag == 'task',
            Template.is_active == True
        ).all()

    def get_publish_templates(self, db: Session) -> List[Template]:
        """Get all publish templates"""
        return db.query(Template).filter(
            Template.tag == 'publish',
            Template.is_active == True
        ).all()

    def create(
        self, 
        db: Session, 
        obj_in: TemplateCreate,
        created_by: Optional[int] = None
    ) -> Template:
        data = obj_in.model_dump(exclude_unset=True)
        applicable_templates = data.pop("applicable_templates", None)

        db_obj = Template(
            **data,
            created_by=created_by,
            updated_by=created_by
        )
        db.add(db_obj)
        db.flush()

        if applicable_templates is not None:
            codes = [c.strip() for c in applicable_templates.split(",") if c.strip()]
            if codes:
                parent_templates = db.query(Template).filter(Template.code.in_(codes)).all()
                db_obj.project_templates = parent_templates
            else:
                db_obj.project_templates = []

        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(
        self, 
        db: Session, 
        db_obj: Template,
        obj_in: TemplateUpdate,
        updated_by: Optional[int] = None
    ) -> Template:
        update_data = obj_in.model_dump(exclude_unset=True)
        applicable_templates = update_data.pop("applicable_templates", None)
        
        if updated_by:
            update_data["updated_by"] = updated_by
            
        for field, value in update_data.items():
            setattr(db_obj, field, value)
            
        if applicable_templates is not None:
            codes = [c.strip() for c in applicable_templates.split(",") if c.strip()]
            if codes:
                parent_templates = db.query(Template).filter(Template.code.in_(codes)).all()
                db_obj.project_templates = parent_templates
            else:
                db_obj.project_templates = []
            
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def soft_delete(self, db: Session, id: int) -> Optional[Template]:
        obj = self.get(db, id)
        if obj:
            obj.is_active = False
            db.commit()
        return obj

template = CRUDTemplate()