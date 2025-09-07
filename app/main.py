from contextlib import asynccontextmanager

from db.database import BaseModel, engine
from exceptions.exceptions import AppException
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse


# Асинхронная функция для инициализации базы данных
async def init_db():
    async with engine.begin() as conn:
        # Создание таблиц, если их нет
        await conn.run_sync(BaseModel.metadata.create_all)


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()


app = FastAPI(lifespan=lifespan)


@app.exception_handler(AppException)
async def app_exception_handler(request: Request, exc: AppException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"message": exc.message}
    )
