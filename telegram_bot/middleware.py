from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject
from typing import Optional
from provider import provider_user
from provider.models import AccessTokenResponse


class UserMiddleware(BaseMiddleware):

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        user: Optional[AccessTokenResponse] = await provider_user.login_by_telegram_id(
            event.from_user.id
        )
        data["user"] = user
        return await handler(event, data)
