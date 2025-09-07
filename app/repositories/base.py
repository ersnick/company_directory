import logging
from typing import List, Optional, Type, TypeVar, Generic
from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError


logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Универсальный generic для моделей
T = TypeVar("T")


class BaseRepository(Generic[T]):
    """Базовый класс с CRUD методами"""

    def __init__(self, model: Type[T]):
        self.model = model

    async def get_all(self, db: AsyncSession) -> List[T]:
        try:
            result = await db.execute(select(self.model))
            return result.scalars().all()
        except SQLAlchemyError as e:
            logger.error("Ошибка при получении всех объектов %s: %s", self.model.__name__, e)
            return []

    async def get_by_id(self, db: AsyncSession, obj_id: int) -> Optional[T]:
        try:
            result = await db.execute(
                select(self.model).where(self.model.id == obj_id)
            )
            return result.scalars().first()
        except SQLAlchemyError as e:
            logger.error("Ошибка при получении объекта %s по id=%s: %s",
                         self.model.__name__, obj_id, e)
            return None

    async def create(self, db: AsyncSession, obj: T) -> Optional[T]:
        try:
            db.add(obj)
            await db.commit()
            await db.refresh(obj)
            logger.info("Создан объект %s id=%s", self.model.__name__, obj.id)
            return obj
        except SQLAlchemyError as e:
            await db.rollback()
            logger.error("Ошибка при создании объекта %s: %s", self.model.__name__, e)
            return None

    async def update(self, db: AsyncSession, obj_id: int, updates: dict) -> Optional[T]:
        try:
            result = await db.execute(
                update(self.model)
                .where(self.model.id == obj_id)
                .values(**updates)
                .returning(self.model)
            )
            await db.commit()
            obj = result.scalars().first()
            if obj:
                logger.info("Обновлён объект %s id=%s", self.model.__name__, obj_id)
            return obj
        except SQLAlchemyError as e:
            await db.rollback()
            logger.error("Ошибка при обновлении объекта %s id=%s: %s",
                         self.model.__name__, obj_id, e)
            return None

    async def delete(self, db: AsyncSession, obj_id: int) -> bool:
        try:
            result = await db.execute(
                delete(self.model).where(self.model.id == obj_id).returning(self.model.id)
            )
            await db.commit()
            deleted_id = result.scalar()
            if deleted_id:
                logger.info("Удалён объект %s id=%s", self.model.__name__, deleted_id)
                return True
            return False
        except SQLAlchemyError as e:
            await db.rollback()
            logger.error("Ошибка при удалении объекта %s id=%s: %s",
                         self.model.__name__, obj_id, e)
            return False
