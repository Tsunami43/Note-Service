from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, ARRAY
from database import Base


class NoteModel(Base):
    __tablename__ = "notes"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    content = Column(String)
    tags = Column(ARRAY(String), nullable=True)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)

    # Добавляем поле user_id с внешним ключом на таблицу пользователей
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
