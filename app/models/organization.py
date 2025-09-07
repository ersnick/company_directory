from typing import List
from sqlalchemy import String, Integer, ForeignKey, UniqueConstraint, Index, Boolean, Column, Table
from sqlalchemy.orm import Mapped, mapped_column, relationship
from db.database import BaseModel

from models.activity import Activity

organization_activity = Table(
    "organization_activity",
    BaseModel.metadata,
    Column("organization_id", ForeignKey("organizations.id", ondelete="CASCADE"), primary_key=True),
    Column("activity_id", ForeignKey("activities.id", ondelete="CASCADE"), primary_key=True),
    UniqueConstraint("organization_id", "activity_id", name="uq_org_activity"),
)


class Organization(BaseModel):
    __tablename__ = "organizations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)

    building_id: Mapped[int] = mapped_column(
        ForeignKey("buildings.id", ondelete="RESTRICT"), nullable=False
    )
    building: Mapped["Building"] = relationship(
        back_populates="organizations",
        lazy="joined",
    )

    phones: Mapped[List["OrganizationPhone"]] = relationship(
        back_populates="organization",
        cascade="all, delete-orphan",
        order_by="OrganizationPhone.position",
        passive_deletes=True,
        lazy="selectin",
    )

    activities: Mapped[List["Activity"]] = relationship(
        secondary=organization_activity,
        back_populates="organizations",
        lazy="selectin",
    )

    __table_args__ = (
        UniqueConstraint("name", "building_id", name="uq_organizations_name_building"),
        Index("ix_organizations_name", "name"),
    )

    def __repr__(self) -> str:
        return f"Organization(id={self.id!r}, name={self.name!r})"


class OrganizationPhone(BaseModel):
    __tablename__ = "organization_phones"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    organization_id: Mapped[int] = mapped_column(
        ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False
    )
    organization: Mapped["Organization"] = relationship(back_populates="phones")

    phone: Mapped[str] = mapped_column(String(64), nullable=False)
    position: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    is_primary: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    __table_args__ = (
        UniqueConstraint("organization_id", "phone", name="uq_org_phone_unique"),
        Index("ix_org_phones_org_pos", "organization_id", "position"),
    )

    def __repr__(self) -> str:
        return f"OrganizationPhone(id={self.id!r}, phone={self.phone!r})"
