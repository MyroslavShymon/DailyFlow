from daily_flow.ui.telegram.handlers.common_mood_log.get import perform_common_mood_log_get
from daily_flow.ui.telegram.handlers.mood_log.delete import perform_mood_log_delete
from daily_flow.ui.telegram.handlers.mood_log.get import perform_mood_log_get
from daily_flow.ui.telegram.runtime import router
from daily_flow.ui.telegram.states import CommonMoodGetForm, MoodGetForm, MoodDeleteForm
from daily_flow.ui.telegram.utils.date_selection import DateAction, DATE_PATTERN

from aiogram import types, F
from aiogram.fsm.context import FSMContext
from aiogram.filters import StateFilter

forms_mapping = {
    f"common_mood_log:{DateAction.GET}": CommonMoodGetForm,
    f"mood_log:{DateAction.GET}": MoodGetForm,
    f"mood_log:{DateAction.DELETE}": MoodDeleteForm,
}

func_mappings = {
    f"common_mood_log:{DateAction.GET}": perform_common_mood_log_get,
    f"mood_log:{DateAction.GET}": perform_mood_log_get,
    f"mood_log:{DateAction.DELETE}": perform_mood_log_delete,
}

@router.callback_query(
    StateFilter(*{f.waiting_for_date for f in forms_mapping.values()}),
    F.data.startswith("date_")
)
async def process_date_selection(
        callback: types.CallbackQuery,
        state: FSMContext
):
    await callback.answer()

    selected_data = callback.data[5:]
    state_val, action_val, date_val = selected_data.split(":", 2)

    if date_val == "manual":
        form = forms_mapping.get(f"{state_val}:{action_val}")
        if not form:
            await callback.message.answer("❌ Невідома дія/форма")
            return

        await state.set_state(form.waiting_for_date)

        await callback.message.answer("Введи дату в форматі 25-12-2006:")
        await callback.message.edit_reply_markup(reply_markup=None)
        return
    func_key = f"{state_val}:{action_val}"

    executor = func_mappings.get(func_key)

    if executor:
        await executor(callback.message, date_val, state)
    else:
        await callback.message.answer("❌ Дія не підтримується")

    await callback.message.delete()

@router.message(
    StateFilter(*{f.waiting_for_date for f in forms_mapping.values()}),
    ~F.text.regexp(DATE_PATTERN.pattern)
)
async def process_wrong_date_format(message: types.Message):
    await message.answer("⚠️ Це не схоже на дату. Будь ласка, введи дату або натисни кнопку 'Скасувати'.")
