import config
import os
from fastapi import FastAPI
from loguru import logger
from api import user, note
from database import Database

app = FastAPI()

# Инициализация базы данных
db = Database()


@app.on_event("startup")
async def on_startup():
    logger.info("Запуск приложения...")
    await db.init_db()


@app.on_event("shutdown")
async def on_shutdown():
    logger.info("Выключение приложения...")


# Подключение роутеров
app.include_router(user.router, prefix="/api")
app.include_router(note.router, prefix="/api")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host=os.getenv("HOST_APP"), port=int(os.getenv("PORT_APP")))
