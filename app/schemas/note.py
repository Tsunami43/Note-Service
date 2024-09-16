from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime


class NoteCreate(BaseModel):
    title: str
    content: str
    tags: Optional[List[str]] = []


class NoteUpdate(BaseModel):
    title: Optional[str]
    content: Optional[str]
    tags: Optional[List[str]]


class NoteResponse(BaseModel):
    id: int
    title: str
    content: str
    tags: Optional[List[str]]
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True
