import os
import aiohttp
from loguru import logger
from typing import List, Optional
from .models import NoteResponse, NoteCreate, NoteUpdate


BASE_URL = f"http://{os.getenv('HOST_APP')}:{os.getenv('PORT_APP')}/api"


async def create_note(token: str, note_data: NoteCreate) -> Optional[NoteResponse]:
    url = f"{BASE_URL}/notes/"
    headers = {"Authorization": f"Bearer {token}"}

    async with aiohttp.ClientSession() as session:
        try:
            logger.info("Отправка запроса на создание заметки")
            async with session.post(
                url, json=note_data.dict(), headers=headers
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    logger.info(f"Заметка успешно создана: {data}")
                    return NoteResponse(**data)
                else:
                    logger.error(
                        f"Ошибка при создании заметки. Статус: {response.status}"
                    )
                    logger.debug(f"Тело ответа: {await response.text()}")
        except Exception as e:
            logger.error(f"Исключение при создании заметки: {e}")


async def read_note(token: str, note_id: int) -> Optional[NoteResponse]:
    url = f"{BASE_URL}/notes/{note_id}"
    headers = {"Authorization": f"Bearer {token}"}

    async with aiohttp.ClientSession() as session:
        try:
            logger.info(f"Отправка запроса на получение заметки с ID: {note_id}")
            async with session.get(url, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    logger.info(f"Заметка успешно получена: {data}")
                    return NoteResponse(**data)
                elif response.status == 404:
                    logger.warning(f"Заметка с ID {note_id} не найдена")
                else:
                    logger.error(
                        f"Ошибка при получении заметки. Статус: {response.status}"
                    )
                    logger.debug(f"Тело ответа: {await response.text()}")
        except Exception as e:
            logger.error(f"Исключение при получении заметки: {e}")


async def update_note(
    token: str, note_id: int, note_data: NoteUpdate
) -> Optional[NoteResponse]:
    url = f"{BASE_URL}/notes/{note_id}"
    headers = {"Authorization": f"Bearer {token}"}

    async with aiohttp.ClientSession() as session:
        try:
            logger.info(f"Отправка запроса на обновление заметки с ID: {note_id}")
            async with session.put(
                url, json=note_data.dict(exclude_unset=True), headers=headers
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    logger.info(f"Заметка успешно обновлена: {data}")
                    return NoteResponse(**data)
                elif response.status == 404:
                    logger.warning(f"Заметка с ID {note_id} не найдена")
                else:
                    logger.error(
                        f"Ошибка при обновлении заметки. Статус: {response.status}"
                    )
                    logger.debug(f"Тело ответа: {await response.text()}")
        except Exception as e:
            logger.error(f"Исключение при обновлении заметки: {e}")


async def delete_note(token: str, note_id: int) -> bool:
    url = f"{BASE_URL}/notes/{note_id}"
    headers = {"Authorization": f"Bearer {token}"}

    async with aiohttp.ClientSession() as session:
        try:
            logger.info(f"Отправка запроса на удаление заметки с ID: {note_id}")
            async with session.delete(url, headers=headers) as response:
                if response.status == 200:
                    logger.info(f"Заметка с ID {note_id} успешно удалена")
                    return True
                elif response.status == 404:
                    logger.warning(f"Заметка с ID {note_id} не найдена")
                else:
                    logger.error(
                        f"Ошибка при удалении заметки. Статус: {response.status}"
                    )
                    logger.debug(f"Тело ответа: {await response.text()}")
        except Exception as e:
            logger.error(f"Исключение при удалении заметки: {e}")
    return False


async def search_notes_by_tag(token: str, tag: str) -> List[NoteResponse]:
    url = f"{BASE_URL}/notes/tag/{tag}"
    headers = {"Authorization": f"Bearer {token}"}

    async with aiohttp.ClientSession() as session:
        try:
            logger.info(f"Отправка запроса на поиск заметок с тегом '{tag}'")
            async with session.get(url, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    logger.info(f"Заметки с тегом '{tag}' успешно получены: {data}")
                    return [NoteResponse(**note) for note in data]
                elif response.status == 404:
                    logger.warning(f"Заметки с тегом '{tag}' не найдены")
                else:
                    logger.error(
                        f"Ошибка при поиске заметок с тегом '{tag}'. Статус: {response.status}"
                    )
                    logger.debug(f"Тело ответа: {await response.text()}")
        except Exception as e:
            logger.error(f"Исключение при поиске заметок с тегом '{tag}': {e}")


async def get_all_notes(token: str) -> List[NoteResponse]:
    url = f"{BASE_URL}/notes/"
    headers = {"Authorization": f"Bearer {token}"}

    async with aiohttp.ClientSession() as session:
        try:
            logger.info(f"Отправка запроса на получение всех заметок")
            async with session.get(url, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    logger.info(f"Заметки успешно получены: {data}")
                    return [NoteResponse(**note) for note in data]
                elif response.status == 404:
                    logger.warning(f"Заметки не найдены")
                else:
                    logger.error(
                        f"Ошибка при получении заметок. Статус: {response.status}"
                    )
                    logger.debug(f"Тело ответа: {await response.text()}")
        except Exception as e:
            logger.error(f"Исключение при получении заметок: {e}")
