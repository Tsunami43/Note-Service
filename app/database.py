import os
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from loguru import logger
from sqlalchemy.exc import SQLAlchemyError

Base = declarative_base()


class Database:
    def __init__(self):
        self.engine = create_async_engine(os.getenv("DATABASE_URL"), echo=False)
        self.SessionLocal = sessionmaker(
            autocommit=False, autoflush=False, bind=self.engine, class_=AsyncSession
        )

    async def get_session(self):
        try:
            async with self.SessionLocal() as session:
                logger.info("Создание сессии для работы с базой данных")
                yield session
        except SQLAlchemyError as e:  # чтобы мы не поймали ошибку от роутеров
            logger.error(f"Ошибка при создании сессии: {e}")
            raise e

    async def init_db(self):
        """Инициализация базы данных, создание всех таблиц"""
        try:
            async with self.engine.begin() as conn:
                logger.info("Инициализация базы данных...")
                await conn.run_sync(Base.metadata.create_all)
                logger.info("База данных инициализирована.")
        except Exception as e:
            logger.error(f"Ошибка при инициализации базы данных: {e}")
            raise e

    async def drop_db(self):
        """Удаление всех таблиц из базы данных"""
        try:
            async with self.engine.begin() as conn:
                logger.info("Удаление таблиц из базы данных...")
                await conn.run_sync(Base.metadata.drop_all)
                logger.info("Все таблицы удалены.")
        except Exception as e:
            logger.error(f"Ошибка при удалении таблиц: {e}")
            raise e

    async def clear_db(self):
        """Очистка базы данных (удаление всех записей, но не таблиц)"""
        try:
            async with self.engine.begin() as conn:
                logger.info("Очистка базы данных...")
                for table in reversed(Base.metadata.sorted_tables):
                    await conn.execute(table.delete())
                logger.info("База данных очищена.")
        except Exception as e:
            logger.error(f"Ошибка при очистке базы данных: {e}")
            raise e
