import os
import aiohttp
from loguru import logger
from .models import UserCreate, AccessTokenResponse
from typing import Union

BASE_URL = f"http://{os.getenv('HOST_APP')}:{os.getenv('PORT_APP')}/api"


async def create_user(
    username: str, password: str, telegram_id: int
) -> Union[UserCreate, None]:
    url = f"{BASE_URL}/register"
    payload = {"username": username, "password": password, "telegram_id": telegram_id}
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload) as response:
                if response.status == 200:
                    result = await response.json()
                    user = UserCreate(**result)
                    logger.info("Создание пользователя: %s", user)
                    return user
                else:
                    error_message = await response.text()
                    logger.error("Ошибка создания пользователя: %s", error_message)
                    return None
    except aiohttp.ClientError as e:
        logger.error("Ошибка запроса: %s", e)
        return None


async def login_by_telegram_id(telegram_id: int) -> Union[AccessTokenResponse, None]:
    url = f"{BASE_URL}/login_by_telegram_id"
    payload = {"telegram_id": telegram_id}
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload) as response:
                if response.status == 200:
                    result = await response.json()
                    access_token_response = AccessTokenResponse(**result)
                    logger.info("Логин по Telegram ID: %s", access_token_response)
                    return access_token_response
                else:
                    error_message = await response.text()
                    logger.error("Ошибка логина по Telegram ID: %s", error_message)
                    return None
    except aiohttp.ClientError as e:
        logger.error("Ошибка запроса: %s", e)
        return None


async def update_telegram_id(
    username: str, password: str, new_telegram_id: int
) -> Union[UserCreate, None]:
    url = f"{BASE_URL}/add_telegram"
    payload = {
        "username": username,
        "password": password,
        "telegram_id": new_telegram_id,
    }
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload) as response:
                if response.status == 200:
                    result = await response.json()
                    user = UserCreate(**result)
                    logger.info("Обновление Telegram ID: %s", user)
                    return user
                else:
                    error_message = await response.text()
                    logger.error("Ошибка обновления Telegram ID: %s", error_message)
                    return None
    except aiohttp.ClientError as e:
        logger.error("Ошибка запроса: %s", e)
        return None
