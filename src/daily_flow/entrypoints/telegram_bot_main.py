import asyncio
import logging

from daily_flow.ui.telegram.main import build_telegram_bot_main

logger = logging.getLogger(__name__)


def main() -> None:
    try:
        asyncio.run(build_telegram_bot_main())
    except KeyboardInterrupt:
        logger.info("Бот зупинений")
