import asyncio
import logging
from typing import TypeVar, Callable, Type

from aiogram import types, F, Bot
from aiogram.fsm.context import FSMContext

from daily_flow.db.repositories.common_mood_repo import CommonMoodLog, MoodTagImpact
from daily_flow.db.repositories.mood_log_repo import MoodLog
from daily_flow.services.errors import ServiceError
from daily_flow.ui.telegram.keyboards.main import MainMenu
from daily_flow.ui.telegram.utils.dto import DTO, process_dto
from daily_flow.ui.telegram.utils.forms_state import TGForm, form_get, form_reset


logger = logging.getLogger(__name__)

T = TypeVar("T", CommonMoodLog, MoodLog, MoodTagImpact)

async def form_submit(
        callback: types.CallbackQuery,
        state: FSMContext,
        bot: Bot,
        form_name: str,
        values_to_upsert: list[str],
        dto_class: Type[DTO],
        mapping: dict[str, str],
        upsert_func: Callable[[DTO], T],
        render_func: Callable[..., str]
):
    await callback.answer()

    form: TGForm = await form_get(state, form_name)
    last_msg = form["last_msg"]
    form_values = form["values"]

    last_chat_id = last_msg.get("chat_id")
    last_form_message_id = last_msg.get("message_id")

    if not last_chat_id or not last_form_message_id:
        await callback.message.answer("⚠️ Не знайшов повідомлення форми. Відкрий форму ще раз.")
        return

    values = {k: form_values.get(k) for k in values_to_upsert}

    try:
        dto = await process_dto(
            mapping=mapping,
            values=values,
            dto_class=dto_class,
            callback=callback
        )
        if dto:
            saved = await asyncio.to_thread(upsert_func, dto)
            if saved:
                await bot.delete_message(
                    chat_id=last_chat_id,
                    message_id=last_form_message_id
                )
                await callback.message.answer(f"{render_func(saved, values)}")
                await form_reset(state, form_name)
                await state.set_state(None)
                await callback.message.answer(
                    "✅ Дані збережено! Повертаємось у головне меню:",
                    reply_markup=MainMenu.get()
                )

    except (ServiceError, ValueError) as e:
        logger.error("Service error: %s", e)
        error_text = str(e)
        await callback.message.answer(f"❌ Помилка: {error_text}")