from pydantic import BaseModel


class BuildingSchema(BaseModel):
    id: int
    address: str
    latitude: float
    longitude: float

    class Config:
        orm_mode = True