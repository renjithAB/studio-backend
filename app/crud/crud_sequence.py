from app.crud.base import CRUDBase
from app.models.sequence import Sequence
from app.schemas.sequence import SequenceCreate, SequenceUpdate

class CRUDSequence(CRUDBase[Sequence, SequenceCreate, SequenceUpdate]):
    pass

sequence = CRUDSequence(Sequence)
