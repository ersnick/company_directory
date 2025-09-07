from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, class_mapper
from core.config import settings


# Подключение к базе данных PostgreSQL
engine = create_async_engine(settings.DATABASE_URL, future=True, echo=True)
Base = declarative_base()

# Асинхронная сессия
AsyncSessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,
)


# Асинхронная сессия
async def get_db():
    async with AsyncSessionLocal() as db:
        yield db


class BaseModel(Base):
    __abstract__ = True

    def to_dict(self):
        """
        Преобразует SQLAlchemy-модель в словарь.
        """
        return {
            column.key: getattr(self, column.key)
            for column in class_mapper(self.__class__).columns
        }