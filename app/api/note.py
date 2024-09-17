import os
from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from loguru import logger
from datetime import datetime
from schemas.note import NoteCreate, NoteUpdate, NoteResponse
from models.note import NoteModel
from database import Database
from jose import JWTError, jwt


router = APIRouter()
db = Database()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")


def get_current_user_id(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Не удалось проверить учетные данные",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: int = payload.get("user_id")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    return user_id


@router.post("/notes/", response_model=NoteResponse)
async def create_note(
    note: NoteCreate,
    db: AsyncSession = Depends(db.get_session),
    user_id: int = Depends(get_current_user_id),
):
    try:
        logger.info(f"Создание новой заметки для пользователя с ID: {user_id}")
        db_note = NoteModel(
            **note.dict(),
            user_id=user_id,  # Привязываем заметку к user_id
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        db.add(db_note)
        await db.commit()
        await db.refresh(db_note)
        logger.info(f"Заметка {db_note.id} успешно создана")
        return db_note
    except Exception as e:
        logger.error(f"Ошибка при создании заметки: {e}")
        raise HTTPException(status_code=500, detail="Ошибка при создании заметки")


@router.get("/notes/{note_id}", response_model=NoteResponse)
async def read_note(
    note_id: int,
    db: AsyncSession = Depends(db.get_session),
    user_id: int = Depends(get_current_user_id),
):
    try:
        logger.info(
            f"Запрос на получение заметки с ID: {note_id} для пользователя с ID: {user_id}"
        )
        result = await db.execute(
            select(NoteModel).where(
                NoteModel.id == note_id, NoteModel.user_id == user_id
            )
        )
        note = result.scalars().first()
        if not note:
            logger.warning(
                f"Заметка с ID {note_id} не найдена или не принадлежит пользователю с ID {user_id}"
            )
            raise HTTPException(status_code=404, detail="Заметка не найдена")
        logger.info(f"Заметка с ID {note_id} успешно получена")
        return note
    except Exception as e:
        logger.error(f"Ошибка при получении заметки: {e}")
        raise HTTPException(status_code=500, detail="Ошибка при получении заметки")


@router.put("/notes/{note_id}", response_model=NoteResponse)
async def update_note(
    note_id: int,
    note: NoteUpdate,
    db: AsyncSession = Depends(db.get_session),
    user_id: int = Depends(get_current_user_id),
):
    try:
        logger.info(
            f"Запрос на обновление заметки с ID: {note_id} для пользователя с ID: {user_id}"
        )

        # Получаем заметку по ID
        result = await db.execute(
            select(NoteModel).where(
                NoteModel.id == note_id, NoteModel.user_id == user_id
            )
        )
        db_note = result.scalars().first()

        if not db_note:
            logger.warning(
                f"Заметка с ID {note_id} не найдена или не принадлежит пользователю с ID {user_id}"
            )
            raise HTTPException(status_code=404, detail="Заметка не найдена")

        # Обновляем только предоставленные пользователем поля
        if note.title is not None:
            db_note.title = note.title
        if note.content is not None:
            db_note.content = note.content
        if note.tags is not None:
            db_note.tags = note.tags

        db_note.updated_at = datetime.utcnow()  # Обновляем время модификации

        await db.commit()
        await db.refresh(db_note)

        logger.info(f"Заметка с ID {note_id} успешно обновлена")
        return db_note
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Ошибка при обновлении заметки: {e}")
        raise HTTPException(status_code=500, detail="Ошибка при обновлении заметки")


@router.delete("/notes/{note_id}")
async def delete_note(
    note_id: int,
    db: AsyncSession = Depends(db.get_session),
    user_id: int = Depends(get_current_user_id),
):
    try:
        logger.info(
            f"Запрос на удаление заметки с ID: {note_id} для пользователя с ID: {user_id}"
        )
        result = await db.execute(
            select(NoteModel).where(
                NoteModel.id == note_id, NoteModel.user_id == user_id
            )
        )
        note = result.scalars().first()
        if not note:
            logger.warning(
                f"Заметка с ID {note_id} не найдена или не принадлежит пользователю с ID {user_id}"
            )
            raise HTTPException(status_code=404, detail="Заметка не найдена")
        await db.delete(note)
        await db.commit()
        logger.info(f"Заметка с ID {note_id} успешно удалена")
        return {"detail": "Заметка успешно удалена"}
    except Exception as e:
        logger.error(f"Ошибка при удалении заметки: {e}")
        raise HTTPException(status_code=500, detail="Ошибка при удалении заметки")
