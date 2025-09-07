from db.models import OrganizationPhone
from repositories.base import BaseRepository


class OrganizationPhoneRepository(BaseRepository[OrganizationPhone]):
    def __init__(self):
        super().__init__(OrganizationPhone)
