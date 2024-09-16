from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from loguru import logger
from datetime import datetime
from schemas.note import NoteCreate, NoteUpdate, NoteResponse
from models.note import NoteModel
from database import Database

router = APIRouter()
db = Database()


@router.post("/notes/", response_model=NoteResponse)
async def create_note(note: NoteCreate, db: AsyncSession = Depends(db.get_session)):
    try:
        logger.info(f"Создание новой заметки: {note.title}")
        db_note = NoteModel(
            **note.dict(), created_at=datetime.utcnow(), updated_at=datetime.utcnow()
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
async def read_note(note_id: int, db: AsyncSession = Depends(db.get_session)):
    try:
        logger.info(f"Запрос на получение заметки с ID: {note_id}")
        result = await db.execute(select(NoteModel).where(NoteModel.id == note_id))
        note = result.scalars().first()
        if not note:
            logger.warning(f"Заметка с ID {note_id} не найдена")
            raise HTTPException(status_code=404, detail="Заметка не найдена")
        logger.info(f"Заметка с ID {note_id} успешно получена")
        return note
    except Exception as e:
        logger.error(f"Ошибка при получении заметки: {e}")
        raise HTTPException(status_code=500, detail="Ошибка при получении заметки")


@router.put("/notes/{note_id}", response_model=NoteResponse)
async def update_note(
    note_id: int, note: NoteUpdate, db: AsyncSession = Depends(db.get_session)
):
    try:
        logger.info(f"Запрос на обновление заметки с ID: {note_id}")
        result = await db.execute(select(NoteModel).where(NoteModel.id == note_id))
        db_note = result.scalars().first()
        if not db_note:
            logger.warning(f"Заметка с ID {note_id} не найдена")
            raise HTTPException(status_code=404, detail="Заметка не найдена")
        for key, value in note.dict().items():
            setattr(db_note, key, value)
        db_note.updated_at = datetime.utcnow()
        await db.commit()
        await db.refresh(db_note)
        logger.info(f"Заметка с ID {note_id} успешно обновлена")
        return db_note
    except Exception as e:
        logger.error(f"Ошибка при обновлении заметки: {e}")
        raise HTTPException(status_code=500, detail="Ошибка при обновлении заметки")


@router.delete("/notes/{note_id}")
async def delete_note(note_id: int, db: AsyncSession = Depends(db.get_session)):
    try:
        logger.info(f"Запрос на удаление заметки с ID: {note_id}")
        result = await db.execute(select(NoteModel).where(NoteModel.id == note_id))
        note = result.scalars().first()
        if not note:
            logger.warning(f"Заметка с ID {note_id} не найдена")
            raise HTTPException(status_code=404, detail="Заметка не найдена")
        await db.delete(note)
        await db.commit()
        logger.info(f"Заметка с ID {note_id} успешно удалена")
        return {"detail": "Заметка успешно удалена"}
    except Exception as e:
        logger.error(f"Ошибка при удалении заметки: {e}")
        raise HTTPException(status_code=500, detail="Ошибка при удалении заметки")
