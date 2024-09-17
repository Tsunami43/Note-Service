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
    await message.answer(
        "Для отмены действия /cancel.\n\nВведите тег для поиска заметок:"
    )
    await state.set_state(SearchNoteStates.waiting_for_tag)


# Обработчик ввода тега и поиск заметок через API
@router.message(StateFilter(SearchNoteStates.waiting_for_tag))
async def handle_tag(message: Message, state: FSMContext, user: AccessTokenResponse):
    tag = message.text

    notes = await provider_note.search_notes_by_tag(user.access_token, tag)

    if notes:
        notes_summary = [
            f"📝 <b>Заметка ID:</b> <code>{note.id}</code>\n"
            f"<b>Заголовок:</b> <i>{note.title}</i>\n"
            f"<b>Содержимое:</b> <i>{note.content}</i>\n"
            f"<b>Теги:</b> {', '.join(note.tags) if note.tags else 'Нет тегов'}\n"
            f"<b>Создана:</b> <i>{note.created_at.strftime('%d.%m.%Y %H:%M:%S')}</i>\n"
            f"<b>Обновлена:</b> <i>{note.updated_at.strftime('%d.%m.%Y %H:%M:%S')}</i>\n"
            f"{'-'*40}\n"
            for note in notes
        ]
        result = "\n".join(notes_summary)
        await message.answer(
            f"📚 <b>Количество заметок:</b> <code>{len(notes)}</code>\n\n{result}",
            parse_mode="HTML",
        )
    else:
        await message.answer(f"📭 Заметки с тегом {tag} не найдены.")

    await state.clear()
