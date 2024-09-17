from aiogram import Router, F
from aiogram.filters import Command, StateFilter
from aiogram.types import Message
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from provider import provider_note
from provider.models import AccessTokenResponse


class DeleteNoteStates(StatesGroup):
    waiting_for_note_id = State()


router = Router()


@router.message(Command("delete_note"))
async def start_delete_note_handler(
    message: Message, state: FSMContext, user: AccessTokenResponse
):
    if not user:
        await message.answer(
            "Вы не авторизованы. Пожалуйста, войдите в систему с помощью команды /login."
        )
        return
    await message.answer("Введите ID заметки для удаления:")
    await state.set_state(DeleteNoteStates.waiting_for_note_id)


# Обработчик ввода ID заметки и удаление через API
@router.message(StateFilter(DeleteNoteStates.waiting_for_note_id))
async def handle_note_id(
    message: Message, state: FSMContext, user: AccessTokenResponse
):
    note_id = message.text

    success = await provider_note.delete_note(user.access_token, note_id)

    if success:
        await message.answer(f"Заметка с ID {note_id} успешно удалена.")
    else:
        await message.answer(f"Ошибка при удалении заметки с ID {note_id}.")

    await state.clear()
