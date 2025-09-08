import logging
from typing import List, Optional

from sqlalchemy.ext.asyncio import AsyncSession

from repositories.organization import OrganizationRepository
from models.organization import Organization

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class OrganizationService:
    def __init__(self):
        self.repository = OrganizationRepository()

    async def get_organizations_in_buildings(
        self, db: AsyncSession, building_id: int
    ) -> List[Organization]:
        """Список всех организаций находящихся в конкретном здании"""
        try:
            return await self.repository.get_by_building(db, building_id)
        except Exception as e:
            logger.error("Ошибка при получении организаций в здании %s: %s", building_id, e)
            return []

    async def get_organizations_by_activity(
        self, db: AsyncSession, activity_id: int
    ) -> List[Organization]:
        """Список всех организаций по виду деятельности"""
        try:
            return await self.repository.get_by_activity(db, activity_id)
        except Exception as e:
            logger.error("Ошибка при получении организаций по виду деятельности %s: %s", activity_id, e)
            return []

    async def get_organization_by_id(
        self, db: AsyncSession, org_id: int
    ) -> Optional[Organization]:
        """Вывод информации об организации по её идентификатору"""
        try:
            return await self.repository.get_detailed_by_id(db, org_id)
        except Exception as e:
            logger.error("Ошибка при получении организации по id %s: %s", org_id, e)
            return None

    async def search_organizations_by_activity_tree(
        self, db: AsyncSession, root_activity_id: int
    ) -> List[Organization]:
        """
        Поиск организаций по виду деятельности, включая вложенные (до 3 уровней).
        Например, для "Еда" вернутся также организации с деятельностью
        "Мясная продукция" и "Молочная продукция".
        """
        try:
            return await self.repository.search_by_activity_tree(db, root_activity_id)
        except Exception as e:
            logger.error("Ошибка при поиске организаций по дереву видов деятельности %s: %s", root_activity_id, e)
            return []

    async def search_organizations_by_name(
        self, db: AsyncSession, name: str
    ) -> List[Organization]:
        """Поиск организаций по названию (частичное совпадение, регистронезависимое)"""
        try:
            return await self.repository.search_by_name(db, name)
        except Exception as e:
            logger.error("Ошибка при поиске организаций по имени '%s': %s", name, e)
            return []

    async def get_organizations_in_rectangle(
            self, db: AsyncSession, lat_min: float, lat_max: float, lon_min: float, lon_max: float
    ) -> List[Organization]:
        try:
            orgs = await self.repository.get_in_rectangle(db, lat_min, lat_max, lon_min, lon_max)
            logger.info(
                "Успешно получены %s организаций в прямоугольнике [%s,%s]x[%s,%s]",
                len(orgs), lat_min, lat_max, lon_min, lon_max
            )
            return orgs
        except Exception as e:
            logger.error(
                "Ошибка в сервисе при получении организаций в прямоугольнике [%s,%s]x[%s,%s]: %s",
                lat_min, lat_max, lon_min, lon_max, e
            )
            return []

    async def get_organizations_in_radius(
            self, db: AsyncSession, lat: float, lon: float, radius_km: float
    ) -> List[Organization]:
        try:
            orgs = await self.repository.get_in_radius(db, lat, lon, radius_km)
            logger.info(
                "Успешно получены %s организаций в радиусе %s км от точки (%s, %s)",
                len(orgs), radius_km, lat, lon
            )
            return orgs
        except Exception as e:
            logger.error(
                "Ошибка в сервисе при получении организаций в радиусе (%s, %s), r=%s: %s",
                lat, lon, radius_km, e
            )
            return []
