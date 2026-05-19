from sqlalchemy.orm import Session
from app.models.episode import Episode
from app.schemas.episode import EpisodeCreate, EpisodeUpdate, EpisodeResponse
from typing import Optional, List
from app.models.domain import Domain
import logging

logger = logging.getLogger(__name__)

class EpisodeService:

    def create_episode(
        self,
        db: Session,
        *,
        episode_in: EpisodeCreate,
        created_by: Optional[int] = None
    ) -> EpisodeResponse:
        """Create a new episode."""
        logger.info(f"Creating episode: {episode_in.name} for project {episode_in.project_id}")

        db_obj = Episode(
            code=episode_in.code,
            name=episode_in.name,
            description=episode_in.description,
            project_id=episode_in.project_id,
            domain_id=episode_in.domain_id,
            is_active=episode_in.is_active,
            created_by=created_by,
            updated_by=created_by,
        )
        db.add(db_obj)
        db.flush()

        # 2. If extra nodes requested, create copies for all other episode domains
        if episode_in.create_extra_nodes:
            # Find all domains in this project with code == 'episode'
            episode_domains = db.query(Domain).filter(
                Domain.project_id == episode_in.project_id,
                Domain.code == 'episode'
            ).all()

            # Exclude the domain already used for the primary episode
            for domain in episode_domains:
                if domain.id == episode_in.domain_id:
                    continue

                extra_episode = Episode(
                    code=episode_in.code,
                    name=episode_in.name,
                    description=episode_in.description,
                    project_id=episode_in.project_id,
                    domain_id=domain.id,
                    is_active=episode_in.is_active,
                    created_by=created_by,
                    updated_by=created_by,
                )
                db.add(extra_episode)
                logger.debug(f"Created extra episode for domain {domain.id}")

        # 3. Commit all changes
        db.commit()
        db.refresh(db_obj)

        return db_obj   

    def get_episode(self, db: Session, episode_id: int) -> Optional[Episode]:
        return db.query(Episode).filter(Episode.id == episode_id).first()

    def get_episodes_by_project(
        self, db: Session, project_id: int, skip: int = 0, limit: int = 100
    ) -> List[Episode]:
        return (
            db.query(Episode)
            .filter(Episode.project_id == project_id)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def update_episode(
        self,
        db: Session,
        *,
        episode: Episode,
        episode_in: EpisodeUpdate,
        updated_by: Optional[int] = None
    ) -> Episode:
        update_data = episode_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(episode, field, value)
        episode.updated_by = updated_by
        db.add(episode)
        db.commit()
        db.refresh(episode)
        return episode

    def delete_episode(self, db: Session, episode: Episode) -> None:
        db.delete(episode)
        db.commit()