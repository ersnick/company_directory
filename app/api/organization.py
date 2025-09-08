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


@router.get("/map", response_model=List[OrganizationSchema])
async def list_organizations_map(
    # радиус
    lat: Optional[float] = Query(None, description="Широта центра точки"),
    lon: Optional[float] = Query(None, description="Долгота центра точки"),
    radius_km: Optional[float] = Query(None, description="Радиус поиска (км)"),

    # прямоугольник
    lat_min: Optional[float] = Query(None, description="Минимальная широта"),
    lat_max: Optional[float] = Query(None, description="Максимальная широта"),
    lon_min: Optional[float] = Query(None, description="Минимальная долгота"),
    lon_max: Optional[float] = Query(None, description="Максимальная долгота"),

    db: AsyncSession = Depends(get_db),
    _: None = Depends(api_key_auth),
) -> List[OrganizationSchema]:
    """
    Список организаций по гео-фильтру:
    - По радиусу (lat, lon, radius_km)
    - По прямоугольной области (lat_min, lat_max, lon_min, lon_max)
    """
    try:
        if lat is not None and lon is not None and radius_km is not None:
            logger.info("Запрос организаций по радиусу: lat=%s, lon=%s, radius=%s", lat, lon, radius_km)
            return await organization_service.get_organizations_in_radius(db, lat, lon, radius_km)

        if all(v is not None for v in [lat_min, lat_max, lon_min, lon_max]):
            logger.info(
                "Запрос организаций по прямоугольнику: [%s,%s]x[%s,%s]",
                lat_min, lat_max, lon_min, lon_max
            )
            return await organization_service.get_organizations_in_rectangle(db, lat_min, lat_max, lon_min, lon_max)

        logger.warning("Некорректный запрос: не заданы параметры фильтрации")
        raise HTTPException(
            status_code=400,
            detail="Нужно указать либо параметры радиуса (lat, lon, radius_km), либо прямоугольника (lat_min, lat_max, lon_min, lon_max)",
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Внутренняя ошибка при обработке geo-запроса: %s", e)
        raise HTTPException(status_code=500, detail="Internal Server Error")


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
    Список организаций с поддержкой фильтров (разрешён только один одновременно).
    """
    try:
        filters = [building_id, activity_id, root_activity_id, name]
        filters_set = [f for f in filters if f is not None]

        if len(filters_set) > 1:
            logger.warning(
                "Некорректный запрос: передано несколько фильтров одновременно %s",
                [("building_id", building_id), ("activity_id", activity_id),
                 ("root_activity_id", root_activity_id), ("name", name)]
            )
            raise HTTPException(
                status_code=400,
                detail="Можно указывать только один фильтр одновременно"
            )

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

        organizations = await organization_service.get_all_organizations(db)
        logger.info("Получен общий список организаций, count=%s", len(organizations))
        return organizations

    except HTTPException:
        raise
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
