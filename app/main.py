from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from api import organization
from db.database import engine
from models import building
from exceptions.exceptions import AppException


async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(building.BaseModel.metadata.create_all)


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield


app = FastAPI(
    title="REST API приложения для справочника Организаций, Зданий, Деятельности",
    description="""
API для работы с организациями и зданиями.
Поддерживаются фильтры по зданию, виду деятельности, геолокации и имени.
Возможен поиск организаций по дереву деятельности.
""",
    version="1.0.0",
    contact={
        "name": "Nikita Ershov",
        "email": "ershov-n-a1009@mail.ru",
        "tg": "@ern1ck"
    },
    lifespan=lifespan,
)

app.include_router(organization.router)


@app.exception_handler(AppException)
async def app_exception_handler(request: Request, exc: AppException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"message": exc.message}
    )
