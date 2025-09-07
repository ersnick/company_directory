from repositories.base import BaseRepository
from models.building import Building


class BuildingRepository(BaseRepository[Building]):
    def __init__(self):
        super().__init__(Building)
