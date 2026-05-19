from app.crud.base import CRUDBase
from app.models.library import Library
from app.schemas.library import LibraryCreate, LibraryUpdate

class CRUDLibrary(CRUDBase[Library, LibraryCreate, LibraryUpdate]):
    pass

library = CRUDLibrary(Library)
