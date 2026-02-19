import logging

from aiogram import types, F, Bot
from aiogram.fsm.context import FSMContext

from daily_flow.ui.telegram.constants.activity import activity_usage_mapping
from daily_flow.ui.telegram.keyboards.activity import ActivityMenu
from daily_flow.ui.telegram.runtime import router
from daily_flow.ui.telegram.states import ActivityUsageForm
from daily_flow.ui.telegram.utils.errors import handle_message_error
from daily_flow.ui.telegram.utils.form_render import get_form_keyboard
from daily_flow.ui.telegram.utils.forms_state import (
    TGForm,
    form_get,
    form_set_last_msg,
    form_set_value,
    form_set_current_field,
    refresh_form_message,
    finish_text_input,
)
from daily_flow.ui.telegram.utils.datetime_parse import parse_to_datetime


logger = logging.getLogger(__name__)

ACTIVITY_USAGE_FORM = "activity_usage"

@router.callback_query(F.data.startswith(f"edit_{ACTIVITY_USAGE_FORM}:"))
async def edit_any_activity_usage_field(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer()

    field_name = callback.data.split(":")[1]
    await form_set_current_field(state, ACTIVITY_USAGE_FORM, field_name)

    await callback.message.edit_text(f"Введіть нові дані про {activity_usage_mapping.get(field_name)}:")
    await state.set_state(ActivityUsageForm.waiting_input)

@router.message(ActivityUsageForm.waiting_input)
async def process_activity_usage_input(message: types.Message, state: FSMContext, bot: Bot):
    form: TGForm = await form_get(state, ACTIVITY_USAGE_FORM)
    field_name = form.get("current_field")

    if not field_name:
        await finish_text_input(state, message, ACTIVITY_USAGE_FORM)
        await handle_message_error(message, "Упс! Оберіть поле для редагування ще раз.")
        return

    raw = (message.text or "").strip()
    if not raw:
        await handle_message_error(message, "❌ Значення не може бути порожнім.")
        return

    if field_name == "used_at":
        dt = parse_to_datetime(raw)
        if not dt:
            await handle_message_error(message, "❌ Невірний формат. Використай DD-MM-YYYY або DD-MM-YYYY HH:MM")
            return
        await form_set_value(state, ACTIVITY_USAGE_FORM, "used_at", dt)
    else:
        await form_set_value(state, ACTIVITY_USAGE_FORM, field_name, raw)

    text = await render_upsert_activity_usage(state)
    await refresh_form_message(state=state, bot=bot, text=text, form_name=ACTIVITY_USAGE_FORM, mapping=activity_usage_mapping)

    await finish_text_input(state, message, ACTIVITY_USAGE_FORM)

async def render_upsert_activity_usage(state: FSMContext) -> str:
    form: TGForm = await form_get(state, ACTIVITY_USAGE_FORM)
    values = form["values"]

    def val(k: str) -> str:
        v = values.get(k, None)
        if v is None:
            return "—"
        return str(v)

    text = "📌 **Виконання активності**\n\n"
    text += "\n".join(f"{activity_usage_mapping.get(k).capitalize()}: {val(k)}" for k in activity_usage_mapping.keys())
    return text

@router.message(F.text == ActivityMenu.BTN_ADD_EDIT_ACTIVITY_USAGE)
async def show_activity_usage_upsert_form(message: types.Message, state: FSMContext):
    text = await render_upsert_activity_usage(state)

    sent_message = await message.answer(
        text,
        reply_markup=get_form_keyboard(activity_usage_mapping, ACTIVITY_USAGE_FORM),
        parse_mode="Markdown",
    )

    await form_set_last_msg(state=state, form_name=ACTIVITY_USAGE_FORM, chat_id=sent_message.chat.id, message_id=sent_message.message_id)
    await state.set_state(ActivityUsageForm.waiting_input)
