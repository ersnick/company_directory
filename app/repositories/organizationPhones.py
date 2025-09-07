from repositories.base import BaseRepository
from models.organization import OrganizationPhone


class OrganizationPhoneRepository(BaseRepository[OrganizationPhone]):
    def __init__(self):
        super().__init__(OrganizationPhone)
