from typing import List, Optional

from sqlalchemy import (
    String,
    Integer,
    ForeignKey,
    Table,
    UniqueConstraint,
    CheckConstraint,
    Index,
    Float,
    Text,
    Boolean,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from db.database import BaseModel


organization_activity = Table(
    "organization_activity",
    BaseModel.metadata,
    # В паре составляют PK, чтобы исключить дубликаты
    # Дополнительно ниже задан UniqueConstraint (избыточно, но читабельно)
    mapped_column(
        "organization_id",
        ForeignKey("organizations.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    mapped_column(
        "activity_id",
        ForeignKey("activities.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    UniqueConstraint("organization_id", "activity_id", name="uq_org_activity"),
)


class Building(BaseModel):
    __tablename__ = "buildings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    # Полный человеко-читаемый адрес (город, улица, дом, офис и т.п.)
    address: Mapped[str] = mapped_column(Text, nullable=False)

    # Географические координаты
    latitude: Mapped[float] = mapped_column(Float, nullable=False)
    longitude: Mapped[float] = mapped_column(Float, nullable=False)

    # Индексы и проверки для координат
    __table_args__ = (
        CheckConstraint("latitude >= -90 AND latitude <= 90", name="ck_buildings_lat_range"),
        CheckConstraint("longitude >= -180 AND longitude <= 180", name="ck_buildings_lon_range"),
        Index("ix_buildings_lat_lon", "latitude", "longitude"),
    )

    # Обратная связь к организациям, находящимся в здании
    organizations: Mapped[List[Organization]] = relationship(
        back_populates="building",
        cascade="save-update",
        passive_deletes=True,
    )

    def __repr__(self) -> str:  # pragma: no cover
        return f"Building(id={self.id!r}, address={self.address!r})"


class Activity(BaseModel):
    __tablename__ = "activities"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)

    # Самоссылка для дерева (adjacency list)
    parent_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("activities.id", ondelete="SET NULL"), nullable=True
    )

    # Родитель и дети
    parent: Mapped[Optional[Activity]] = relationship(
        remote_side="Activity.id",
        back_populates="children",
    )
    children: Mapped[List[Activity]] = relationship(
        back_populates="parent",
        cascade="save-update",  # без delete-orphan, чтобы случайно не удалить поддерево
        passive_deletes=True,
    )

    # Связь с организациями (many-to-many)
    organizations: Mapped[List[Organization]] = relationship(
        secondary=organization_activity,
        back_populates="activities",
        lazy="selectin",
    )

    __table_args__ = (
        # В рамках одного родителя имена категорий уникальны (опционально, но удобно)
        UniqueConstraint("parent_id", "name", name="uq_activities_parent_name"),
        Index("ix_activities_parent", "parent_id"),
        Index("ix_activities_name", "name"),
    )

    def __repr__(self) -> str:  # pragma: no cover
        return f"Activity(id={self.id!r}, name={self.name!r}, parent_id={self.parent_id!r})"


class Organization(BaseModel):
    __tablename__ = "organizations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    # Например: ООО "Рога и Копыта"
    name: Mapped[str] = mapped_column(String(255), nullable=False)

    # Ровно одно здание на организацию
    building_id: Mapped[int] = mapped_column(
        ForeignKey("buildings.id", ondelete="RESTRICT"), nullable=False
    )
    building: Mapped[Building] = relationship(
        back_populates="organizations",
        lazy="joined",
    )

    # Телефоны — отдельная таблица (удобно валидировать, сортировать, добавлять флаги)
    phones: Mapped[List[OrganizationPhone]] = relationship(
        back_populates="organization",
        cascade="all, delete-orphan",
        order_by="OrganizationPhone.position",
        passive_deletes=True,
    )

    # Виды деятельности — many-to-many
    activities: Mapped[List[Activity]] = relationship(
        secondary=organization_activity,
        back_populates="organizations",
        lazy="selectin",
    )

    __table_args__ = (
        UniqueConstraint("name", "building_id", name="uq_organizations_name_building"),
        Index("ix_organizations_name", "name"),
    )

    def __repr__(self) -> str:  # pragma: no cover
        return f"Organization(id={self.id!r}, name={self.name!r})"


class OrganizationPhone(BaseModel):
    __tablename__ = "organization_phones"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    organization_id: Mapped[int] = mapped_column(
        ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False
    )
    organization: Mapped[Organization] = relationship(back_populates="phones")

    # Сам номер телефона. Длину можно подстроить под ваши реалии.
    phone: Mapped[str] = mapped_column(String(64), nullable=False)

    # Позиция для упорядочивания (0, 1, 2, ...). Необязательно, но удобно.
    position: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # Флаг основного номера
    is_primary: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    __table_args__ = (
        UniqueConstraint("organization_id", "phone", name="uq_org_phone_unique"),
        Index("ix_org_phones_org_pos", "organization_id", "position"),
    )

    def __repr__(self) -> str:  # pragma: no cover
        return f"OrganizationPhone(id={self.id!r}, phone={self.phone!r})"
