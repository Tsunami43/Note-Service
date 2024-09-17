from aiogram import F, Router
from aiogram.types import Message
from aiogram.filters import Command
from provider.models import AccessTokenResponse
from aiogram.fsm.context import FSMContext

router = Router()


@router.message(Command("start"))
async def handler_start(message: Message, user: AccessTokenResponse):
    if not user:
        await message.answer(
            "Добро пожаловать! Используйте /login для входа или /register для регистрации. Для получения справки /help. Для отмены любого действия /cancel"
        )
        return
    await message.answer("Вы уже авторизованны")


@router.message(Command("help"))
async def help_handler(message: Message):
    help_text = (
        "<b>/start</b> - Начало работы с ботом\n"
        "<b>/help</b> - Получить справку по командам\n"
        "<b>/create_note</b> - Создать заметку\n"
        "<b>/get_all_notes</b> - Получить все заметки\n"
        "<b>/search_notes</b> - Поиск заметок по тегу\n"
        "<b>/update_note</b> - Обновить заметку\n"
        "<b>/delete_note</b> - Удалить заметку\n"
        "<b>/login</b> - Авторизация\n"
        "<b>/register</b> - Регистрация\n"
        "<b>/cancel</b> - Отменить текущие действия"
    )
    await message.answer(help_text, parse_mode="HTML")


@router.message(Command("cancel"))
async def clear_handler(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("Текущие действия очищены.")
