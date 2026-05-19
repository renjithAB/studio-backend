from typing import List, Optional
from sqlalchemy.orm import Session
from app.crud.base import CRUDBase
from app.models.domain import Domain
from app.schemas.domain import DomainCreate, DomainUpdate

class CRUDDomain(CRUDBase[Domain, DomainCreate, DomainUpdate]):
    def get_by_project(self, db: Session, project_id: int) -> List[Domain]:
        return db.query(self.model).filter(self.model.project_id == project_id).all()

domain = CRUDDomain(Domain)
