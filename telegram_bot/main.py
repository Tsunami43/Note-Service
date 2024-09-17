import config
import os
import asyncio
from loguru import logger
from aiogram import Bot, Dispatcher
from handlers import (
    commands,
    login,
    register,
    create_note,
    search_notes,
    get_all_notes,
    update_note,
    delete_note,
)
from middleware import UserMiddleware
from aiogram.types import BotCommand


bot = Bot(os.getenv("BOT_TOKEN"))
dp = Dispatcher()
dp.message.outer_middleware(UserMiddleware())

#
# @dp.error()
# async def error_handler(update: Update, exception: Exception):
#     # Логируем информацию об ошибке
#     logger.error(f"Возникло исключение: {exception}")
#
#     # Если это ошибка API Telegram
#     if isinstance(exception, TelegramAPIError):
#         logger.error(f"Ошибка Telegram API: {exception}")
#
#     await update.message.reply("Произошла ошибка. Пожалуйста, попробуйте позже.")
#


async def set_bot_commands():
    commands = [
        BotCommand(command="/start", description="Начало работы с ботом"),
        BotCommand(command="/help", description="Получить справку по командам"),
        BotCommand(command="/create_note", description="Создать заметку"),
        BotCommand(command="/get_all_notes", description="Получить все заметки"),
        BotCommand(command="/search_notes", description="Поиск заметок по тегу"),
        BotCommand(command="/update_note", description="Обновить заметку"),
        BotCommand(command="/delete_note", description="Удалить заметку"),
        BotCommand(command="/login", description="Авторизация"),
        BotCommand(command="/register", description="Регистрация"),
        BotCommand(command="/cancel", description="Отмена действия"),
    ]
    await bot.set_my_commands(commands)


async def main():
    try:
        # установка пользовательских команд
        await set_bot_commands()
        # Для пропуска ивентов которые пришли, когда бот был неактивен
        await bot.delete_webhook(drop_pending_updates=True)
        # добавляем обработчики
        dp.include_routers(
            commands.router,
            login.router,
            register.router,
            create_note.router,
            search_notes.router,
            delete_note.router,
            update_note.router,
            get_all_notes.router,
        )

        # Запуск бота
        bot_info = await bot.get_me()
        logger.info(f"Starting bot @{bot_info.username}[{bot_info.id}]")
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
    except Exception as exc:
        logger.critical(exc)
        raise
    finally:
        logger.info("Stopping bot")
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())
