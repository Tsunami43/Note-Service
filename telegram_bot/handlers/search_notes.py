from aiogram import Router, F
from aiogram.filters import Command, StateFilter
from aiogram.types import Message
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from provider import provider_note
from provider.models import AccessTokenResponse


class SearchNoteStates(StatesGroup):
    waiting_for_tag = State()


router = Router()


@router.message(Command("search_notes"))
async def start_search_note_handler(
    message: Message, state: FSMContext, user: AccessTokenResponse
):
    if not user:
        await message.answer(
            "Вы не авторизованы. Пожалуйста, войдите в систему с помощью команды /login."
        )
        return
    await message.answer("Введите тег для поиска заметок:")
    await state.set_state(SearchNoteStates.waiting_for_tag)


# Обработчик ввода тега и поиск заметок через API
@router.message(StateFilter(SearchNoteStates.waiting_for_tag))
async def handle_tag(message: Message, state: FSMContext, user: AccessTokenResponse):
    tag = message.text

    notes = await provider_note.search_notes_by_tag(user.access_token, tag)

    if notes:
        result = "\n".join([f"Заметка {note.id}: {note.title}" for note in notes])
        await message.answer(f"Найденные заметки с тегом {tag}:\n{result}")
    else:
        await message.answer(f"Заметки с тегом {tag} не найдены.")

    await state.clear()
