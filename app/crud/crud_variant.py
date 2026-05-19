from typing import Optional
from sqlalchemy.orm import Session
from app.models.variant import Variant
from app.schemas.variant import VariantCreate, VariantUpdate

class CRUDVariant:
    def get(self, db: Session, id: int) -> Optional[Variant]:
        return db.query(Variant).filter(Variant.id == id, Variant.is_active == True).first()

    def create(self, db: Session, *, obj_in: VariantCreate) -> Variant:
        db_obj = Variant(**obj_in.model_dump(exclude={"create_for_all_tasks"}))
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(
        self, db: Session, *, db_obj: Variant, obj_in: VariantUpdate
    ) -> Variant:
        obj_data = obj_in.model_dump(exclude_unset=True)
        for field, value in obj_data.items():
            setattr(db_obj, field, value)
        db.commit()
        db.refresh(db_obj)
        return db_obj

variant = CRUDVariant()
