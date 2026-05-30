from sqlalchemy.orm import Session
from app.models.sequence import Sequence
from app.schemas.sequence import SequenceCreate, SequenceResponse
from typing import Optional
import logging

logger = logging.getLogger(__name__)

class SequenceService:

    def create_sequence(
        self,
        db: Session,
        *,
        sequence_in: SequenceCreate,
        created_by: Optional[int] = None
    ) -> SequenceResponse:
        logger.info(f"Creating sequence: {sequence_in.name} for project {sequence_in.project_id}, episode {sequence_in.episode_id}")
        domain_id = sequence_in.domain_id
        if (not domain_id or domain_id == -100) and sequence_in.episode_id:
            from app.models.episode import Episode
            episode = db.query(Episode).filter(Episode.id == sequence_in.episode_id).first()
            if episode:
                domain_id = episode.domain_id
        elif domain_id == -100:
            from app.models.domain import Domain
            seq_domain = db.query(Domain).filter(Domain.project_id == sequence_in.project_id, Domain.domain_type == 'sequence').first()
            if seq_domain:
                domain_id = seq_domain.id

        db_obj = Sequence(
            code=sequence_in.code,
            name=sequence_in.name,
            description=sequence_in.description,
            project_id=sequence_in.project_id,
            episode_id=sequence_in.episode_id,
            domain_id=domain_id,
            is_active=sequence_in.is_active,
            created_by=created_by,
            updated_by=created_by,
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)

        return db_obj