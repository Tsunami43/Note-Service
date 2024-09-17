from aiogram import Router, F
from aiogram.filters import Command, StateFilter
from aiogram.types import Message
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from provider import provider_note
from provider.models import NoteCreate, AccessTokenResponse


class CreateNoteStates(StatesGroup):
    waiting_for_title = State()
    waiting_for_content = State()
    waiting_for_tags = State()


router = Router()


@router.message(Command("create_note"))
async def start_create_note_handler(
    message: Message, state: FSMContext, user: AccessTokenResponse
):
    if not user:
        await message.answer(
            "Вы не авторизованы. Пожалуйста, войдите в систему с помощью команды /login."
        )
        return
    await message.answer("Для отмены действия /cancel.\n\nВведите заголовок заметки:")
    await state.set_state(CreateNoteStates.waiting_for_title)


# Обработчик ввода заголовка
@router.message(StateFilter(CreateNoteStates.waiting_for_title))
async def handle_title(message: Message, state: FSMContext):
    await state.update_data(title=message.text)
    await message.answer("Введите содержимое заметки:")
    await state.set_state(CreateNoteStates.waiting_for_content)


# Обработчик ввода содержимого
@router.message(StateFilter(CreateNoteStates.waiting_for_content))
async def handle_content(message: Message, state: FSMContext):
    await state.update_data(content=message.text)
    await message.answer("Введите теги через запятую (можно пропустить):")
    await state.set_state(CreateNoteStates.waiting_for_tags)


# Обработчик ввода тегов и создание заметки через API
@router.message(StateFilter(CreateNoteStates.waiting_for_tags))
async def handle_tags(message: Message, state: FSMContext, user: AccessTokenResponse):
    user_data = await state.get_data()
    title = user_data.get("title")
    content = user_data.get("content")
    tags = message.text.split(",") if message.text else []

    note_data = NoteCreate(title=title, content=content, tags=tags)

    note = await provider_note.create_note(user.access_token, note_data)

    if note:
        await message.answer(
            f"✅ <b>Заметка успешно создана:</b>\n"
            f"<b>ID:</b> <code>{note.id}</code>\n"
            f"<b>Заголовок:</b> <i>{note.title}</i>\n"
            f"<b>Содержимое:</b> <i>{note.content}</i>\n"
            f"<b>Теги:</b> {', '.join(note.tags) if note.tags else 'Нет тегов'}\n"
            f"<b>Создана:</b> <i>{note.created_at.strftime('%d.%m.%Y %H:%M:%S')}</i>\n"
            f"<b>Обновлена:</b> <i>{note.updated_at.strftime('%d.%m.%Y %H:%M:%S')}</i>\n",
            parse_mode="HTML",
        )
    else:
        await message.answer("⚠️ Ошибка при создании заметки.")
    await state.clear()
