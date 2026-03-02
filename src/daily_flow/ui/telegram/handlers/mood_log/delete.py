import logging
from datetime import datetime

from aiogram import F, types
from aiogram.fsm.context import FSMContext

from daily_flow.app.container import Container
from daily_flow.ui.telegram.keyboards.mood import MoodMenu
from daily_flow.ui.telegram.runtime import router
from daily_flow.ui.telegram.states import MoodDeleteForm
from daily_flow.ui.telegram.utils.date_selection import DateAction, get_date_keyboard

logger = logging.getLogger(__name__)


async def perform_mood_log_delete(
    message: types.Message, date_str: str, state: FSMContext, db_container: Container
):
    try:
        selected_date = datetime.strptime(date_str, "%d-%m-%Y").date()
        mood_log = await db_container.mood_log_service.get_mood_log_by_day(selected_date)
        if not mood_log:
            await state.clear()
            return await message.answer(
                f"🔍 Схоже, за {date_str} ще немає жодного запису. Видаляти нічого!",
                reply_markup=MoodMenu.get(),
            )

        deleted_count = await db_container.mood_log_service.delete_mood_log_by_day(selected_date)
        if deleted_count > 0:
            await state.clear()
            await message.answer(
                "✅ Дані видалено! Повертаємось у меню настрою:", reply_markup=MoodMenu.get()
            )
    except ValueError:
        await message.answer("❌ Невірний формат. Спробуй ще раз (наприклад: 25-12-2006):")
    except Exception as e:
        logger.error("Service error: %s", e)
        await message.answer("❌ Сталася помилка сервісу.")


@router.message(F.text == MoodMenu.BTN_DELETE_MOOD_LOG)
async def delete_mood_log(message: types.Message, state: FSMContext):
    await state.set_state(MoodDeleteForm.waiting_for_date)
    await message.answer(
        "Будь ласка, обери дату для запису, який треба видалити:",
        reply_markup=get_date_keyboard(DateAction.DELETE, "mood_log"),
        parse_mode="Markdown",
    )
