import os
from fastapi import APIRouter, HTTPException, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from datetime import timedelta, datetime
from passlib.context import CryptContext
from jose import jwt, JWTError
from loguru import logger
from schemas.user import (
    UserCreate,
    UserLogin,
    AddUserTelegram,
    LoginWithTelegram,
    UserResponse,
)
from models.user import UserModel
from database import Database
from slowapi import Limiter
from slowapi.util import get_remote_address


router = APIRouter()
db = Database()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
limiter = Limiter(key_func=get_remote_address)


SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def authenticate_user(db: AsyncSession, username: str, password: str):
    logger.info(f"Попытка аутентификации пользователя: {username}")
    try:
        result = await db.execute(
            select(UserModel).where(UserModel.username == username)
        )
        user = result.scalars().first()
        if not user or not verify_password(password, user.hashed_password):
            logger.warning(f"Неверные учетные данные для пользователя: {username}")
            return False
        return user
    except Exception as e:
        logger.error(f"Ошибка аутентификации: {e}")
        raise HTTPException(status_code=500, detail="Ошибка сервера")


@router.post("/register", response_model=UserResponse)
@limiter.limit("3/minute")
async def create_user(
    request: Request, user: UserCreate, db: AsyncSession = Depends(db.get_session)
):
    try:
        logger.info(f"Создание пользователя: {user.username}")
        db_user = UserModel(
            username=user.username,
            hashed_password=get_password_hash(user.password),
            telegram_id=user.telegram_id,  # Устанавливаем telegram_id
        )
        db.add(db_user)
        await db.commit()
        await db.refresh(db_user)
        logger.info(f"Пользователь {user.username} успешно создан")
        return db_user
    except Exception as e:
        logger.error(f"Ошибка создания пользователя: {e}")
        raise HTTPException(status_code=500, detail="Ошибка создания пользователя")


@router.post("/login", response_model=dict)
@limiter.limit("3/minute")
async def login_for_access_token(
    request: Request, form_data: UserLogin, db: AsyncSession = Depends(db.get_session)
):
    user = await authenticate_user(db, form_data.username, form_data.password)
    if not user:
        logger.warning(f"Неверное имя пользователя или пароль: {form_data.username}")
        raise HTTPException(
            status_code=401,
            detail="Неверное имя пользователя или пароль",
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"user_id": user.id}, expires_delta=access_token_expires
    )
    logger.info(f"Пользователь {user.username} успешно аутентифицирован")
    return {"access_token": access_token}


@router.post("/add_telegram", response_model=UserResponse)
@limiter.limit("3/minute")
async def update_telegram_id_with_credentials(
    request: Request,
    form_data: AddUserTelegram,
    db: AsyncSession = Depends(db.get_session),
):
    try:
        logger.info(f"Обновление telegram_id для пользователя: {form_data.username}")

        # Аутентификация пользователя
        user = await authenticate_user(db, form_data.username, form_data.password)
        if not user:
            logger.warning(
                f"Неверное имя пользователя или пароль: {form_data.username}"
            )
            raise HTTPException(
                status_code=401, detail="Неверное имя пользователя или пароль"
            )

        # Обновление telegram_id
        user.telegram_id = form_data.telegram_id
        db.add(user)
        await db.commit()
        await db.refresh(user)
        logger.info(f"Telegram ID пользователя {user.username} успешно обновлен")
        return user
    except Exception as e:
        logger.error(f"Ошибка обновления telegram_id: {e}")
        raise HTTPException(status_code=500, detail="Ошибка обновления telegram_id")


async def authenticate_user_by_telegram_id(db: AsyncSession, telegram_id: str):
    logger.info(f"Попытка аутентификации пользователя по telegram_id: {telegram_id}")
    try:
        result = await db.execute(
            select(UserModel).where(UserModel.telegram_id == telegram_id)
        )
        user = result.scalars().first()
        if not user:
            logger.warning(f"Пользователь с telegram_id {telegram_id} не найден")
            return False
        return user
    except Exception as e:
        logger.error(f"Ошибка аутентификации: {e}")
        raise HTTPException(status_code=500, detail="Ошибка сервера")


@router.post("/login_by_telegram_id", response_model=dict)
async def login_by_telegram_id(
    form_data: LoginWithTelegram, db: AsyncSession = Depends(db.get_session)
):
    user = await authenticate_user_by_telegram_id(db, form_data.telegram_id)
    if not user:
        logger.warning(f"Пользователь с telegram_id {form_data.telegram_id} не найден")
        raise HTTPException(
            status_code=401,
            detail="Пользователь с telegram_id не найден",
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"user_id": user.id}, expires_delta=access_token_expires
    )
    logger.info(
        f"Пользователь с telegram_id {form_data.telegram_id} успешно аутентифицирован"
    )
    return {"access_token": access_token}
