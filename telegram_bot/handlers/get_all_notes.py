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
        await message.answer("📭 У вас нет заметок.")
