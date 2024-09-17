from typing import Optional
from pydantic import BaseModel


class UserCreate(BaseModel):
    username: str
    telegram_id: Optional[int] = None


class AccessTokenResponse(BaseModel):
    access_token: str
