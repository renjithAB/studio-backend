from sqlalchemy.orm import Session
from app.models.shot import Shot
from app.schemas.shot import ShotCreate, ShotResponse

from app.models.sequence import Sequence
from app.models.episode import Episode
from typing import Optional, List
import logging

logger = logging.getLogger(__name__)

class ShotService:

    def create_shot(
        self,
        db: Session,
        *,
        shot_in: ShotCreate,
        created_by: Optional[int] = None
    ) -> ShotResponse:
        logger.info(f"Creating shot: {shot_in.name} for sequence {shot_in.sequence_id}")
        domain_id = shot_in.domain_id
        if (not domain_id or domain_id == -100) and shot_in.sequence_id:
            from app.models.sequence import Sequence
            sequence = db.query(Sequence).filter(Sequence.id == shot_in.sequence_id).first()
            if sequence:
                domain_id = sequence.domain_id

        db_obj = Shot(
            code=shot_in.code,
            name=shot_in.name,
            description=shot_in.description,
            project_id=shot_in.project_id,
            sequence_id=shot_in.sequence_id,
            domain_id=domain_id,
            frame_start=shot_in.frame_start,
            frame_end=shot_in.frame_end,
            is_active=shot_in.is_active,
            created_by=created_by,
            updated_by=created_by,
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)

        # 2. Create the Associated Tasks if provided
        if shot_in.tasks:
            # Resolve domain_id (typically from the episode or standard for shot)
            from app.models.sequence import Sequence
            sequence = db.get(Sequence, shot_in.sequence_id)
            from app.models.task import Task
            for task_code in shot_in.tasks:
                task_obj = Task(
                    code=task_code,
                    name=task_code.capitalize(),
                    project_id=shot_in.project_id,
                    domain_id=domain_id,
                    episode_id=sequence.episode_id if sequence else None,
                    sequence_id=shot_in.sequence_id,
                    shot_id=db_obj.id,
                    is_active=True
                )
                db.add(task_obj)
            db.commit()

        return db_obj