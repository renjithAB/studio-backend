from app.crud.base import CRUDBase
from app.models.cycle import Cycle
from app.schemas.cycle import CycleCreate, CycleUpdate

class CRUDCycle(CRUDBase[Cycle, CycleCreate, CycleUpdate]):
    pass

cycle = CRUDCycle(Cycle)
