from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from provider import provider_note
from provider.models import AccessTokenResponse

router = Router()


@router.message(Command("get_all_notes"))
async def get_all_notes_handler(
    message: Message, state: FSMContext, user: AccessTokenResponse
):
    if not user:
        await message.answer(
            "Вы не авторизованы. Пожалуйста, войдите в систему с помощью команды /login."
        )
        return

    notes = await provider_note.get_all_notes(user.access_token)

    if notes:
        result = "\n".join([f"Заметка {note.id}: {note.title}" for note in notes])
        await message.answer(f"Все ваши заметки:\n{result}")
    else:
        await message.answer("У вас нет заметок.")
