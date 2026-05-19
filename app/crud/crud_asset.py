# app/crud/crud_asset.py

from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import and_

from app.models.asset import Asset
from app.schemas.asset import AssetCreate, AssetUpdate

class CRUDAsset:

    def get(self, db: Session, id: int) -> Optional[Asset]:
        return db.query(Asset).filter(
            Asset.id == id,
            Asset.is_active == True
        ).first()

    def get_by_code(self, db: Session, *, project_id: int, code: str) -> Optional[Asset]:
        return db.query(Asset).filter(
            and_(
                Asset.project_id == project_id,
                Asset.code == code,
                Asset.is_active == True
            )
        ).first()

    def get_multi(
        self, db: Session,
        skip: int = 0,
        limit: int = 100,
        project_id: Optional[int] = None,
        category_id: Optional[int] = None,
        domain_id: Optional[int] = None,
    ) -> List[Asset]:
        q = db.query(Asset).filter(Asset.is_active == True)
        
        if project_id:
            q = q.filter(Asset.project_id == project_id)
        if category_id:
            q = q.filter(Asset.category_id == category_id)
            
        return q.order_by(Asset.code).offset(skip).limit(limit).all()

    def get_by_category(
        self, db: Session, *, project_id: int, category_id: int, skip: int = 0, limit: int = 100
    ) -> List[Asset]:
        return db.query(Asset).filter(
            and_(
                Asset.project_id == project_id,
                Asset.category_id == category_id,
                Asset.is_active == True
            )
        ).order_by(Asset.code).offset(skip).limit(limit).all()

    def create(
        self, db: Session, *,
        obj_in: AssetCreate,
        created_by: Optional[int] = None,
    ) -> Asset:
        # obj_in must include domain_id and category_id. template_id is optional.
        db_obj = Asset(
            **obj_in.model_dump(exclude={"tasks", "domain_id"}),
            created_by=created_by,
            updated_by=created_by
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(
        self, db: Session, *,
        db_obj: Asset,
        obj_in: AssetUpdate,
        updated_by: Optional[int] = None,
    ) -> Asset:
        update_data = obj_in.model_dump(exclude_unset=True)
        update_data["updated_by"] = updated_by
        for field, value in update_data.items():
            setattr(db_obj, field, value)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def soft_delete(self, db: Session, *, id: int) -> Optional[Asset]:
        obj = self.get(db, id)
        if obj:
            obj.is_active = False
            db.commit()
        return obj

asset = CRUDAsset()