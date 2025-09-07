from typing import List, Optional
from sqlalchemy import String, Integer, ForeignKey, UniqueConstraint, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from db.database import BaseModel


class Activity(BaseModel):
    __tablename__ = "activities"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)

    parent_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("activities.id", ondelete="SET NULL"), nullable=True
    )

    parent: Mapped[Optional["Activity"]] = relationship(
        remote_side="Activity.id",
        back_populates="children",
    )
    children: Mapped[List["Activity"]] = relationship(
        back_populates="parent",
        cascade="save-update",
        passive_deletes=True,
    )

    organizations: Mapped[List["Organization"]] = relationship(
        secondary="organization_activity",   # тут указываем имя таблицы как строку
        back_populates="activities",
        lazy="selectin",
    )

    __table_args__ = (
        UniqueConstraint("parent_id", "name", name="uq_activities_parent_name"),
        Index("ix_activities_parent", "parent_id"),
        Index("ix_activities_name", "name"),
    )

    def __repr__(self) -> str:
        return f"Activity(id={self.id!r}, name={self.name!r}, parent_id={self.parent_id!r})"
