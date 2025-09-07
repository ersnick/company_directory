import logging
from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession

from services.organization import OrganizationService
from db.database import get_db
from schemas.organization import OrganizationSchema
from core.auth import api_key_auth

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)
router = APIRouter(prefix="/organizations")
organization_service = OrganizationService()


@router.get("/", response_model=List[OrganizationSchema])
async def list_organizations(
    building_id: Optional[int] = Query(None, description="Фильтр по зданию"),
    activity_id: Optional[int] = Query(None, description="Фильтр по виду деятельности"),
    root_activity_id: Optional[int] = Query(None, description="Фильтр по дереву деятельности"),
    name: Optional[str] = Query(None, min_length=1, description="Поиск по имени (частичное совпадение, регистронезависимое)"),
    db: AsyncSession = Depends(get_db),
    _: None = Depends(api_key_auth),
) -> List[OrganizationSchema]:
    """
    Список организаций с поддержкой фильтров:
    - building_id: фильтр по зданию
    - activity_id: фильтр по виду деятельности
    - root_activity_id: фильтр по дереву деятельности (включая вложенные, до 3 уровней)
    - name: поиск по названию (частичное совпадение, регистронезависимое)
    """
    try:
        if building_id is not None:
            organizations = await organization_service.get_organizations_in_buildings(db, building_id)
            logger.info("Получены организации для здания id=%s, count=%s", building_id, len(organizations))
            return organizations

        if activity_id is not None:
            organizations = await organization_service.get_organizations_by_activity(db, activity_id)
            logger.info("Получены организации для деятельности id=%s, count=%s", activity_id, len(organizations))
            return organizations

        if root_activity_id is not None:
            organizations = await organization_service.search_organizations_by_activity_tree(db, root_activity_id)
            logger.info("Поиск организаций по дереву деятельности id=%s, найдено=%s", root_activity_id, len(organizations))
            return organizations

        if name is not None:
            organizations = await organization_service.search_organizations_by_name(db, name)
            logger.info("Поиск организаций по имени='%s', найдено=%s", name, len(organizations))
            return organizations

        # Если фильтры не заданы — вернём все организации (или можно сделать 400)
        organizations = await organization_service.get_all_organizations(db)
        logger.info("Получен общий список организаций, count=%s", len(organizations))
        return organizations

    except Exception as e:
        logger.error("Ошибка при получении списка организаций: %s", e)
        raise HTTPException(status_code=500, detail="Internal Server Error")


@router.get("/{org_id}", response_model=OrganizationSchema)
async def get_organization_by_id(
    org_id: int,
    db: AsyncSession = Depends(get_db),
    _: None = Depends(api_key_auth),
) -> OrganizationSchema:
    """Получение информации об организации по её идентификатору"""
    try:
        organization: Optional[OrganizationSchema] = await organization_service.get_organization_by_id(db, org_id)
        if not organization:
            logger.warning("Организация не найдена id=%s", org_id)
            raise HTTPException(status_code=404, detail="Organization not found")
        logger.info("Получена организация id=%s", org_id)
        return organization
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Ошибка при получении организации id=%s: %s", org_id, e)
        raise HTTPException(status_code=500, detail="Internal Server Error")
