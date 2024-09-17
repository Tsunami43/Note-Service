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


async def main():
    try:
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
