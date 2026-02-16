import asyncio
import logging

from aiogram import Bot

from daily_flow.config.config import BOT_TOKEN
from daily_flow.ui.telegram import handlers
from daily_flow.ui.telegram.runtime import router, dp

logger = logging.getLogger(__name__)

if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN is missing. Put it into .env")

async def main():
    bot = Bot(BOT_TOKEN)
    dp.include_router(router)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())