from collections.abc import Awaitable, Callable
from typing import Any

from aiogram import BaseMiddleware
from aiogram.types import Message, TelegramObject

from daily_flow.config.config import ADMIN_TG_ID


class AuthMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        user_id = event.from_user.id

        if int(user_id) != ADMIN_TG_ID:
            if isinstance(event, Message):
                await event.answer("У вас немає доступу до цього бота. 🛑")
            return

        result = await handler(event, data)

        return result
