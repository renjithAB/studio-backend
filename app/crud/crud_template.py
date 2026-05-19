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
        query = db.query(Template).filter(Template.is_active == True)
            
        return query.order_by(Template.code).offset(skip).limit(limit).all()

    def get_domain_templates_for_project(
        self, 
        db: Session, 
        project_id: int
    ) -> List[Template]:
        """Get all domain templates that apply to a specific project"""
        
        # For JSONB containment with integer IDs, we need to cast to text in the JSON array
        # Since project_ids is a JSONB array of integers, we can use the @> operator directly with an integer array
        return db.query(Template).filter(
            and_(
                Template.tier == 'domainTemplate',
                Template.is_active == True,
                Template.project_ids.op('@>')(f'[{project_id}]')  # JSONB containment with integer
            )
        ).all()

    def get_category_templates(self, db: Session) -> List[Template]:
        """Get all category templates"""
        return db.query(Template).filter(
            Template.tier == 'categoryTemplate',
            Template.is_active == True
        ).all()

    def get_task_templates(self, db: Session) -> List[Template]:
        """Get all task templates"""
        return db.query(Template).filter(
            Template.tier == 'taskTemplate',
            Template.is_active == True
        ).all()

    def get_publish_templates(self, db: Session) -> List[Template]:
        """Get all publish templates"""
        return db.query(Template).filter(
            Template.tier == 'publishTemplate',
            Template.is_active == True
        ).all()

    def create(
        self, 
        db: Session, 
        obj_in: TemplateCreate,
        created_by: Optional[int] = None
    ) -> Template:
        db_obj = Template(
            **obj_in.model_dump(exclude_unset=True),
            created_by=created_by,
            updated_by=created_by
        )
        db.add(db_obj)
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
        if updated_by:
            update_data["updated_by"] = updated_by
            
        for field, value in update_data.items():
            setattr(db_obj, field, value)
            
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