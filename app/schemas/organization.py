from typing import List, Optional
from pydantic import BaseModel

from schemas.building import BuildingSchema
from schemas.activity import ActivitySchema


class OrganizationPhoneSchema(BaseModel):
    id: int
    phone: str
    position: int
    is_primary: bool

    class Config:
        orm_mode = True


class OrganizationSchema(BaseModel):
    id: int
    name: str
    building: BuildingSchema
    phones: List[OrganizationPhoneSchema] = []
    activities: List[ActivitySchema] = []

    class Config:
        orm_mode = True
