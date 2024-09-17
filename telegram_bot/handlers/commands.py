from aiogram import F, Router
from aiogram.types import Message
from aiogram.filters import Command
from provider.models import AccessTokenResponse


router = Router()


@router.message(Command("start"))
async def handler_start(message: Message, user: AccessTokenResponse):
    if not user:
        await message.answer(
            "Добро пожаловать! Используйте /login для входа или /register для регистрации."
        )
        return
    await message.answer("Вы уже авторизованны")
