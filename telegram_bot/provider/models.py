from typing import Optional, List
from pydantic import BaseModel
from datetime import datetime


class UserCreate(BaseModel):
    username: str
    telegram_id: Optional[int] = None


class AccessTokenResponse(BaseModel):
    access_token: str


class NoteCreate(BaseModel):
    title: str
    content: str
    tags: Optional[List[str]] = []


class NoteUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    tags: Optional[List[str]] = None


class NoteResponse(BaseModel):
    id: int
    title: str
    content: str
    tags: Optional[List[str]]
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True
