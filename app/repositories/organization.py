import logging
from typing import List, Optional

from sqlalchemy import select, func
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError

from repositories.base import BaseRepository

from models.activity import Activity
from models.building import Building
from models.organization import Organization

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class OrganizationRepository(BaseRepository[Organization]):
    def __init__(self):
        super().__init__(Organization)

    async def get_by_building(
        self, db: AsyncSession, building_id: int
    ) -> List[Organization]:
        try:
            result = await db.execute(
                select(Organization)
                .where(Organization.building_id == building_id)
                .options(selectinload(Organization.activities), selectinload(Organization.phones))
            )
            orgs = result.scalars().all()
            logger.info("Найдено %s организаций в здании id=%s", len(orgs), building_id)
            return orgs
        except SQLAlchemyError as e:
            logger.error("Ошибка при получении организаций по building_id=%s: %s", building_id, e)
            return []

    async def get_by_activity(
        self, db: AsyncSession, activity_id: int
    ) -> List[Organization]:
        try:
            result = await db.execute(
                select(Organization)
                .join(Organization.activities)
                .where(Activity.id == activity_id)
            )
            orgs = result.scalars().all()
            logger.info("Найдено %s организаций по activity_id=%s", len(orgs), activity_id)
            return orgs
        except SQLAlchemyError as e:
            logger.error("Ошибка при получении организаций по activity_id=%s: %s", activity_id, e)
            return []

    async def get_in_rectangle(
        self,
        db: AsyncSession,
        lat_min: float,
        lat_max: float,
        lon_min: float,
        lon_max: float,
    ) -> List[Organization]:
        try:
            result = await db.execute(
                select(Organization)
                .join(Organization.building)
                .where(
                    (Building.latitude >= lat_min)
                    & (Building.latitude <= lat_max)
                    & (Building.longitude >= lon_min)
                    & (Building.longitude <= lon_max)
                )
            )
            orgs = result.scalars().all()
            logger.info(
                "Найдено %s организаций в прямоугольнике [%s,%s]x[%s,%s]",
                len(orgs), lat_min, lat_max, lon_min, lon_max
            )
            return orgs
        except SQLAlchemyError as e:
            logger.error("Ошибка при поиске организаций в прямоугольнике: %s", e)
            return []

    async def get_in_radius(
        self, db: AsyncSession, lat: float, lon: float, radius_km: float
    ) -> List[Organization]:
        try:
            earth_radius = 6371  # км
            result = await db.execute(
                select(Organization)
                .join(Organization.building)
                .where(
                    earth_radius
                    * func.acos(
                        func.cos(func.radians(lat))
                        * func.cos(func.radians(Building.latitude))
                        * func.cos(func.radians(Building.longitude) - func.radians(lon))
                        + func.sin(func.radians(lat))
                        * func.sin(func.radians(Building.latitude))
                    )
                    <= radius_km
                )
            )
            orgs = result.scalars().all()
            logger.info(
                "Найдено %s организаций в радиусе %s км от точки (%s, %s)",
                len(orgs), radius_km, lat, lon
            )
            return orgs
        except SQLAlchemyError as e:
            logger.error("Ошибка при поиске организаций в радиусе: %s", e)
            return []

    async def get_detailed_by_id(
        self, db: AsyncSession, org_id: int
    ) -> Optional[Organization]:
        try:
            result = await db.execute(
                select(Organization)
                .options(
                    selectinload(Organization.building),
                    selectinload(Organization.phones),
                    selectinload(Organization.activities),
                )
                .where(Organization.id == org_id)
            )
            org = result.scalars().first()
            if org:
                logger.info("Получена детальная информация об организации id=%s", org_id)
            else:
                logger.warning("Организация id=%s не найдена", org_id)
            return org
        except SQLAlchemyError as e:
            logger.error("Ошибка при получении организации id=%s: %s", org_id, e)
            return None

    async def search_by_name(self, db: AsyncSession, name: str) -> List[Organization]:
        try:
            result = await db.execute(
                select(Organization).where(Organization.name.ilike(f"%{name}%"))
            )
            orgs = result.scalars().all()
            logger.info("Найдено %s организаций по имени '%s'", len(orgs), name)
            return orgs
        except SQLAlchemyError as e:
            logger.error("Ошибка при поиске организаций по имени '%s': %s", name, e)
            return []

    async def search_by_activity_tree(
        self, db: AsyncSession, root_activity_id: int
    ) -> List[Organization]:
        try:
            async def get_children_ids(act_id: int, level: int = 1) -> List[int]:
                if level > 3:
                    return []
                result = await db.execute(
                    select(Activity).where(Activity.parent_id == act_id)
                )
                children = result.scalars().all()
                ids = [c.id for c in children]
                for child in children:
                    ids.extend(await get_children_ids(child.id, level + 1))
                return ids

            activity_ids = [root_activity_id] + await get_children_ids(root_activity_id)

            result = await db.execute(
                select(Organization)
                .join(Organization.activities)
                .where(Activity.id.in_(activity_ids))
                .distinct()
            )
            orgs = result.scalars().all()
            logger.info(
                "Найдено %s организаций по дереву activity_id=%s (вкл. вложенные)",
                len(orgs), root_activity_id
            )
            return orgs
        except SQLAlchemyError as e:
            logger.error("Ошибка при поиске организаций по дереву activity_id=%s: %s",
                         root_activity_id, e)
            return []
