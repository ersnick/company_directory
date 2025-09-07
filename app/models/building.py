from typing import List
from sqlalchemy import Integer, Text, Float, CheckConstraint, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from db.database import BaseModel

from models.organization import Organization


class Building(BaseModel):
    __tablename__ = "buildings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    address: Mapped[str] = mapped_column(Text, nullable=False)

    latitude: Mapped[float] = mapped_column(Float, nullable=False)
    longitude: Mapped[float] = mapped_column(Float, nullable=False)

    __table_args__ = (
        CheckConstraint("latitude >= -90 AND latitude <= 90", name="ck_buildings_lat_range"),
        CheckConstraint("longitude >= -180 AND longitude <= 180", name="ck_buildings_lon_range"),
        Index("ix_buildings_lat_lon", "latitude", "longitude"),
    )

    organizations: Mapped[List["Organization"]] = relationship(
        back_populates="building",
        cascade="save-update",
        passive_deletes=True,
    )

    def __repr__(self) -> str:
        return f"Building(id={self.id!r}, address={self.address!r})"
