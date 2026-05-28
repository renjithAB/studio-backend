from typing import List, Optional
from sqlalchemy.orm import Session, joinedload
from app.models.project import Project
from app.schemas.project import ProjectCreate, ProjectUpdate

class CRUDProject:

    def get(self, db: Session, id: int) -> Optional[Project]:
        return db.query(Project).options(joinedload(Project.template)).filter(
            Project.id == id,
            Project.is_active == True
        ).first()

    def get_by_code(self, db: Session, code: str, exclude_id: Optional[int] = None) -> Optional[Project]:
        q = db.query(Project).filter(Project.code == code)
        if exclude_id:
            q = q.filter(Project.id != exclude_id)
        return q.first()

    def get_multi(
        self, db: Session,
        skip: int = 0,
        limit: int = 100,
        type: Optional[str] = None,
    ) -> List[Project]:
        q = db.query(Project).options(joinedload(Project.template)).filter(Project.is_active == True)
        if type:
            q = q.filter(Project.type == type)
        return q.order_by(Project.created_at.desc()).offset(skip).limit(limit).all()

    def create(
        self, db: Session, *,
        obj_in: ProjectCreate,
        created_by: Optional[int] = None,
    ) -> Project:
        db_obj = Project(
            **obj_in.model_dump(),
            created_by=created_by,
            updated_by=created_by,
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(
        self, db: Session, *,
        db_obj: Project,
        obj_in: ProjectUpdate,
        updated_by: Optional[int] = None,
    ) -> Project:
        update_data = obj_in.model_dump(exclude_unset=True)
        update_data["updated_by"] = updated_by
        for field, value in update_data.items():
            setattr(db_obj, field, value)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def soft_delete(self, db: Session, *, id: int) -> Optional[Project]:
        obj = self.get(db, id)
        if obj:
            obj.is_active = False
            db.commit()
        return obj

project = CRUDProject()