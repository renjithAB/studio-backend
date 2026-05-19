from sqlalchemy.orm import Session
from app.models.publish_types import PublishType
from app.schemas.publish_types import PublishTypeCreate, PublishTypeResponse
import logging
from typing import Optional

logger = logging.getLogger(__name__)

class PublishTypeService:
    
    def create_publish_type(
        self,
        db: Session,
        *,
        publish_type_in: PublishTypeCreate,
        created_by: Optional[int] = None
    ) -> PublishTypeResponse:
        """Create a new publish type."""
        
        logger.info(f"Creating publish type: {publish_type_in.name} ({publish_type_in.code})")
        
        db_obj = PublishType(
            code=publish_type_in.code,
            name=publish_type_in.name,
            description=publish_type_in.description,
            project_id=publish_type_in.project_id,
            variant_id=publish_type_in.variant_id,
            task_id=publish_type_in.task_id,
            publish_type_code=publish_type_in.publish_type_code,
            is_active=publish_type_in.is_active,
            created_by=created_by,
            updated_by=created_by,
        )
        
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        
        logger.info(f"✓ Publish type created with ID: {db_obj.id}")
        
        return db_obj  # FastAPI will convert to PublishTypeResponse via ORM mode