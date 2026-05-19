from app.crud.base import CRUDBase
from app.models.shot import Shot
from app.schemas.shot import ShotCreate, ShotUpdate

class CRUDShot(CRUDBase[Shot, ShotCreate, ShotUpdate]):
    pass

shot = CRUDShot(Shot)
