import config
import os
import asyncio
from loguru import logger
from aiogram import Bot, Dispatcher
from handlers import router

bot = Bot(os.getenv("BOT_TOKEN")
dp = Dispatcher()

async def main():
    try:
        # Для пропуска ивентов которые пришли, когда бот был неактивен
        await bot.delete_webhook(drop_pending_updates=True)
        # добавляем обработчики
        dp.include_router(router)
    
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

if __name__=="__main__":
    asyncio.run(main())    
