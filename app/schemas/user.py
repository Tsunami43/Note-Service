from pydantic import BaseModel
from typing import Optional


class UserCreate(BaseModel):
    username: str
    password: str
    telegram_id: Optional[int] = None


class UserLogin(UserCreate):
    pass


class AddUserTelegram(UserCreate):
    pass


class UserResponse(BaseModel):
    id: int
    username: str

    class Config:
        orm_mode = True


class LoginWithTelegram(BaseModel):
    telegram_id: int
