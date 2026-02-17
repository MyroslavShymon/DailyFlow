from daily_flow.ui.telegram.handlers.common_mood_log.get import perform_common_mood_log_get
from daily_flow.ui.telegram.handlers.common_mood_log.tag.delete import perform_tag_impact_delete
from daily_flow.ui.telegram.handlers.common_mood_log.tag.get import perform_tag_impact_get
from daily_flow.ui.telegram.handlers.mood_log.delete import perform_mood_log_delete
from daily_flow.ui.telegram.handlers.mood_log.get import perform_mood_log_get
from daily_flow.ui.telegram.runtime import router
from daily_flow.ui.telegram.states import CommonMoodGetForm, MoodGetForm, MoodDeleteForm, TagImpactGetForm, \
    TagImpactDeleteForm
from daily_flow.ui.telegram.utils.date_selection import DateAction, DATE_PATTERN

from aiogram import types, F
from aiogram.fsm.context import FSMContext
from aiogram.filters import StateFilter

from daily_flow.ui.telegram.utils.payload import unpack_optional

FORMS_MAPPING = {
    f"common_mood_log:{DateAction.GET}": CommonMoodGetForm,
    f"mood_log:{DateAction.GET}": MoodGetForm,
    f"mood_log:{DateAction.DELETE}": MoodDeleteForm,
    f"tag_impact:{DateAction.GET}": TagImpactGetForm,
    f"tag_impact:{DateAction.DELETE}": TagImpactDeleteForm,
}

FUNC_MAPPING = {
    f"common_mood_log:{DateAction.GET}": lambda message, state, date_val, opt: perform_common_mood_log_get(message=message, state=state, date_str=date_val),
    f"mood_log:{DateAction.GET}": lambda message, state, date_val, opt: perform_mood_log_get(message=message, state=state, date_str=date_val),
    f"mood_log:{DateAction.DELETE}": lambda message, state, date_val, opt: perform_mood_log_delete(message=message, state=state, date_str=date_val),
    f"tag_impact:{DateAction.GET}": lambda message, state, date_val, opt: perform_tag_impact_get(message=message, state=state, date_str=date_val),
    f"tag_impact:{DateAction.DELETE}": lambda message, state, date_val, opt: perform_tag_impact_delete(
        message=message,
        state=state,
        date_str=date_val,
        tag=(opt.get("tag") or None),
    ),
}

DATE_CTX_KEY = "date_ctx_key"
DATE_OPT_KEY = "date_optional_vals"

@router.callback_query(F.data.startswith("date_"))
async def process_date_selection(
        callback: types.CallbackQuery,
        state: FSMContext
):
    await callback.answer()

    payload = callback.data[5:]
    if "###" in payload:
        selected_part, opt_part = payload.split("###", 1)
    else:
        selected_part, opt_part = payload, ""
    entity, action, date_val = selected_part.split(":", 2)

    ctx_key = f"{entity}:{action}"
    optional_vals = unpack_optional(opt_part)

    if date_val == "manual":
        form = FORMS_MAPPING.get(ctx_key)
        if not form:
            await callback.message.answer("❌ Невідома дія/форма")
            return

        await state.update_data({DATE_CTX_KEY: ctx_key, DATE_OPT_KEY: optional_vals})
        await state.set_state(form.waiting_for_date)

        await callback.message.answer("Введи дату в форматі 25-12-2006:")
        await callback.message.edit_reply_markup(reply_markup=None)
        return

    executor = FUNC_MAPPING.get(ctx_key)

    if not executor:
        await callback.message.answer("❌ Дія не підтримується")
        return

    await executor(callback.message, state, date_val, optional_vals)
    await state.clear()
    await callback.message.delete()

@router.message(
    StateFilter(*{f.waiting_for_date for f in FORMS_MAPPING.values()}),
    F.text.regexp(DATE_PATTERN.pattern)
)
async def process_manual_date_ok(message: types.Message, state: FSMContext):
    data = await state.get_data()
    ctx_key = data.get(DATE_CTX_KEY)
    optional_vals = data.get(DATE_OPT_KEY, {})

    if not ctx_key:
        await message.answer("⚠️ Не розумію, для якої дії ця дата. Почни ще раз.")
        await state.clear()
        return

    executor = FUNC_MAPPING.get(ctx_key)
    if not executor:
        await message.answer("❌ Дія не підтримується")
        await state.clear()
        return

    await executor(message, state, message.text, optional_vals)

@router.message(
    StateFilter(*{f.waiting_for_date for f in FORMS_MAPPING.values()}),
    ~F.text.regexp(DATE_PATTERN.pattern)
)
async def process_wrong_date_format(message: types.Message):
    await message.answer("⚠️ Це не схоже на дату. Будь ласка, введи дату або натисни кнопку 'Скасувати'.")
