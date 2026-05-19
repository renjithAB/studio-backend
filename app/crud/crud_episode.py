from app.crud.base import CRUDBase
from app.models.episode import Episode
from app.schemas.episode import EpisodeCreate, EpisodeUpdate

class CRUDEpisode(CRUDBase[Episode, EpisodeCreate, EpisodeUpdate]):
    pass

episode = CRUDEpisode(Episode)
