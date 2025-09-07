from pydantic import BaseModel
from typing import Optional


class ActivitySchema(BaseModel):
    id: int
    name: str
    parent_id: Optional[int]

    class Config:
        orm_mode = True
