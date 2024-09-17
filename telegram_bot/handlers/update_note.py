from aiogram import Router, F
from aiogram.filters import Command, StateFilter
from aiogram.types import Message
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from provider import provider_note
from provider.models import NoteUpdate, AccessTokenResponse


class UpdateNoteStates(StatesGroup):
    waiting_for_note_id = State()
    waiting_for_title = State()
    waiting_for_content = State()


router = Router()


@router.message(Command("update_note"))
async def start_update_note_handler(
    message: Message, state: FSMContext, user: AccessTokenResponse
):
    if not user:
        await message.answer(
            "Вы не авторизованы. Пожалуйста, войдите в систему с помощью команды /login."
        )
        return
    await message.answer(
        "Для отмены действия /cancel.\n\nВведите ID заметки для обновления:"
    )
    await state.set_state(UpdateNoteStates.waiting_for_note_id)


# Обработчик ввода ID заметки
@router.message(StateFilter(UpdateNoteStates.waiting_for_note_id))
async def handle_note_id(message: Message, state: FSMContext):
    await state.update_data(note_id=message.text)
    await message.answer(
        "Введите новый заголовок (или оставьте пустым, если не нужно изменять):"
    )
    await state.set_state(UpdateNoteStates.waiting_for_title)


# Обработчик ввода нового заголовка
@router.message(StateFilter(UpdateNoteStates.waiting_for_title))
async def handle_title(message: Message, state: FSMContext):
    await state.update_data(title=message.text)
    await message.answer(
        "Введите новое содержимое (или оставьте пустым, если не нужно изменять):"
    )
    await state.set_state(UpdateNoteStates.waiting_for_content)


# Обработчик ввода нового содержимого и обновление заметки через API
@router.message(StateFilter(UpdateNoteStates.waiting_for_content))
async def handle_content(
    message: Message, state: FSMContext, user: AccessTokenResponse
):
    user_data = await state.get_data()
    note_id = user_data.get("note_id")
    title = user_data.get("title") or None
    content = message.text or None

    note_data = NoteUpdate(title=title, content=content)

    note = await provider_note.update_note(user.access_token, note_id, note_data)

    if note:
        await message.answer(
            f"✅ <b>Заметка успешно обновлена:</b>\n"
            f"<b>ID:</b> <code>{note.id}</code>\n"
            f"<b>Заголовок:</b> <i>{note.title}</i>\n"
            f"<b>Содержимое:</b> <i>{note.content}</i>\n"
            f"<b>Теги:</b> {', '.join(note.tags) if note.tags else 'Нет тегов'}\n"
            f"<b>Создана:</b> <i>{note.created_at.strftime('%d.%m.%Y %H:%M:%S')}</i>\n"
            f"<b>Обновлена:</b> <i>{note.updated_at.strftime('%d.%m.%Y %H:%M:%S')}</i>\n",
            parse_mode="HTML",
        )
    else:
        await message.answer("⚠️ Ошибка при обновлении заметки.")

    await state.clear()
