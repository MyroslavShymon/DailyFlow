import asyncio
import logging

from aiogram import Bot

from daily_flow.ui.telegram import handlers
from daily_flow.app.container import build_container
from daily_flow.config.config import BOT_TOKEN
from daily_flow.config.db import load_db_settings
from daily_flow.ui.telegram.runtime import router, dp

logger = logging.getLogger(__name__)

async def main():
    settings = load_db_settings()
    db_container = build_container(settings)

    if not BOT_TOKEN:
        raise RuntimeError("BOT_TOKEN is missing. Put it into .env")

    bot = Bot(BOT_TOKEN)

    dp.include_router(router)

    logger.info("Бот запускається...")

    await bot.delete_webhook(drop_pending_updates=True)

    await dp.start_polling(bot, db_container=db_container)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Бот зупинений")