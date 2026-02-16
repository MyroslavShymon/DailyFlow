import logging
from datetime import datetime

from aiogram import types, F
from aiogram.fsm.context import FSMContext

from daily_flow.ui.telegram.keyboards.mood import MoodMenu
from daily_flow.ui.telegram.render.mood_log import render_mood_log
from daily_flow.ui.telegram.runtime import router, c
from daily_flow.ui.telegram.states import MoodGetForm
from daily_flow.ui.telegram.utils.date_selection import DATE_PATTERN, DateAction, get_date_keyboard

logger = logging.getLogger(__name__)

@router.message(MoodGetForm.waiting_for_date, F.text.regexp(DATE_PATTERN))
async def get_mood_log_message(message: types.Message, state: FSMContext):
    await perform_mood_log_get(message, message.text, state)

async def perform_mood_log_get(message: types.Message, date_str: str, state: FSMContext):
    try:
        selected_date = datetime.strptime(date_str, "%d-%m-%Y").date()
        mood_log = c.mood_log_service.get_mood_log_by_day(selected_date)

        await state.clear()

        if not mood_log:
            await message.answer(
                f"🔍 Схоже, за {date_str} ще немає жодного запису.",
                reply_markup=MoodMenu.get()
            )
        else:
            await message.answer(
                "🔍 Ось результат пошуку: \n" + render_mood_log(mood_log),
                reply_markup = MoodMenu.get()
            )
    except ValueError:
        await message.answer("❌ Невірний формат. Спробуй ще раз (наприклад: 25-12-2006):")
    except Exception as e:
        logger.error("Service error: %s", e)
        await message.answer(f"❌ Сталася помилка сервісу.")

@router.message(F.text == MoodMenu.BTN_GET_MOOD_LOG)
async def get_mood_log(message: types.Message, state: FSMContext):
    await state.set_state(MoodGetForm.waiting_for_date)
    await message.answer(
        "Будь ласка, обери дату для запису, який треба переглянути:",
        reply_markup=get_date_keyboard(DateAction.GET, "mood_log"),
        parse_mode="Markdown"
    )