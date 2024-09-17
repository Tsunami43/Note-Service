from aiogram import F, Router
from aiogram.types import Message
from aiogram.filters import Command

router = Router()


@router.message(Command("start"))
async def handler_start(message: Message):
    pass
