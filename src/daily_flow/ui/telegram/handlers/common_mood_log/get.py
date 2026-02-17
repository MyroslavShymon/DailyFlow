import logging
from datetime import datetime

from aiogram import types, F
from aiogram.fsm.context import FSMContext

from daily_flow.ui.telegram.keyboards.common_mood import CommonMoodMenu
from daily_flow.ui.telegram.runtime import c, router
from daily_flow.ui.telegram.render.сommon_mood_log import render_common_mood_log
from daily_flow.ui.telegram.states import CommonMoodGetForm
from daily_flow.ui.telegram.utils.date_selection import get_date_keyboard, DateAction


logger = logging.getLogger(__name__)

async def perform_common_mood_log_get(message: types.Message, date_str: str, state: FSMContext):
    try:
        selected_date = datetime.strptime(date_str, "%d-%m-%Y").date()
        common_mood_log = c.common_mood_log_service.get_common_mood_by_day(selected_date)

        await state.clear()

        if not common_mood_log:
            await message.answer(
                f"🔍 Схоже, за {date_str} ще немає жодного запису.",
                reply_markup=CommonMoodMenu.get()
            )
        else:
            await message.answer(
                "🔍 Ось результат пошуку: \n" + render_common_mood_log(common_mood_log),
                reply_markup=CommonMoodMenu.get()
            )
    except ValueError:
        await message.answer("❌ Невірний формат. Спробуй ще раз (наприклад: 25-12-2006):")
    except Exception as e:
        logger.error("Service error: %s", e)
        await message.answer(f"❌ Сталася помилка сервісу.")


@router.message(F.text == CommonMoodMenu.BTN_GET_COMMON_MOOD_LOG)
async def get_common_mood_log(message: types.Message, state: FSMContext):
    await state.set_state(CommonMoodGetForm.waiting_for_date)
    await message.answer(
        "Будь ласка, обери дату для запису, який треба переглянути:",
        reply_markup=get_date_keyboard(DateAction.GET, "common_mood_log"),
        parse_mode="Markdown"
    )