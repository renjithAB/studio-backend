from app.crud.base import CRUDBase
from app.models.publish_types import PublishType
from app.schemas.publish_types import PublishTypeCreate, PublishTypeUpdate

class CRUDPublishType(CRUDBase[PublishType, PublishTypeCreate, PublishTypeUpdate]):
    pass

publish_type = CRUDPublishType(PublishType)
