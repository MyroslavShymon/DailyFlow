from typing import Callable, Any, Dict, Awaitable

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, Message

from daily_flow.config.config import ADMIN_TG_ID


class AuthMiddleware(BaseMiddleware):
    async def __call__(
            self,
            handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
            event: TelegramObject,
            data: Dict[str, Any]
    ) -> Any:
        user_id = event.from_user.id

        if int(user_id) != ADMIN_TG_ID:
            if isinstance(event, Message):
                await event.answer("У вас немає доступу до цього бота. 🛑")
            return

        result = await handler(event, data)

        return result