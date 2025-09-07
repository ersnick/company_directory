from db.models import Building
from repositories.base import BaseRepository


class BuildingRepository(BaseRepository[Building]):
    def __init__(self):
        super().__init__(Building)
