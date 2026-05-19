from app.crud.base import CRUDBase
from app.models.editorial import Editorial
from app.schemas.editorial import EditorialCreate, EditorialUpdate

class CRUDEditorial(CRUDBase[Editorial, EditorialCreate, EditorialUpdate]):
    pass

editorial = CRUDEditorial(Editorial)
