import logging
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError

from repositories.base import BaseRepository
from app.models.activity import Activity

logger = logging.getLogger(__name__)


class ActivityRepository(BaseRepository[Activity]):
    def __init__(self):
        super().__init__(Activity)

    async def create_with_level_check(self, db: AsyncSession, activity: Activity) -> Activity:
        """
        Создать Activity с проверкой уровня вложенности (максимум 3).
        """
        try:
            # Проверяем глубину вложенности
            level = 1
            parent = activity.parent
            while parent:
                level += 1
                if level > 3:
                    raise ValueError("Максимальная вложенность видов деятельности — 3 уровня")
                parent = parent.parent

            db.add(activity)
            await db.commit()
            await db.refresh(activity)

            logger.info("Создана Activity id=%s name='%s'", activity.id, activity.name)
            return activity

        except ValueError as ve:
            await db.rollback()
            logger.warning("Не удалось создать Activity (ограничение по вложенности): %s", ve)
            raise

        except SQLAlchemyError as e:
            await db.rollback()
            logger.error("Ошибка при создании Activity name='%s': %s", activity.name, e)
            raise
