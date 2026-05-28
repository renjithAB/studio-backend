from typing import Optional
from sqlalchemy.orm import Session
from app.models.version import Version
from app.schemas.version import VersionCreate, VersionUpdate

class CRUDVersion:
    def get(self, db: Session, id: int) -> Optional[Version]:
        return db.query(Version).filter(Version.id == id, Version.is_active == True).first()

    def create(self, db: Session, *, obj_in: VersionCreate, created_by: Optional[int] = None) -> Version:
        # Generate sequential code starting from 000001
        from sqlalchemy import text
        try:
            next_val = db.execute(text("SELECT nextval('version_code_seq')")).scalar()
            code_seq = f"{next_val:06d}"
        except Exception:
            from sqlalchemy import func
            max_id = db.query(func.max(Version.id)).scalar() or 0
            code_seq = f"{max_id + 1:06d}"

        db_obj = Version(
            code=code_seq,
            name=obj_in.name,
            version_number=obj_in.version_number,
            project_id=obj_in.project_id,
            publish_id=obj_in.publish_id,
            asset_id=obj_in.asset_id,
            category_id=obj_in.category_id,
            variant_id=obj_in.variant_id,
            task_id=obj_in.task_id,
            episode_id=obj_in.episode_id,
            sequence_id=obj_in.sequence_id,
            shot_id=obj_in.shot_id,
            library_id=obj_in.library_id,
            cycle_id=obj_in.cycle_id,
            editorial_id=obj_in.editorial_id,
            description=obj_in.description,
            tag=obj_in.tag,
            thumbnail_url=obj_in.thumbnail_url,
            movie_url=obj_in.movie_url,
            is_active=obj_in.is_active,
            created_by=created_by,
            updated_by=created_by
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(
        self, db: Session, *, db_obj: Version, obj_in: VersionUpdate, updated_by: Optional[int] = None
    ) -> Version:
        obj_data = obj_in.model_dump(exclude_unset=True)
        for field, value in obj_data.items():
            setattr(db_obj, field, value)
        if updated_by is not None:
            db_obj.updated_by = updated_by
        db.commit()
        db.refresh(db_obj)
        return db_obj

version = CRUDVersion()
