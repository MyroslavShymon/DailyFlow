import logging

from aiogram import types, F, Bot
from aiogram.fsm.context import FSMContext

from daily_flow.ui.telegram.constants.activity import category_mapping
from daily_flow.ui.telegram.keyboards.activity import ActivityMenu
from daily_flow.ui.telegram.runtime import router
from daily_flow.ui.telegram.states import CategoryForm
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

logger = logging.getLogger(__name__)

CATEGORY_FORM = "category"

@router.callback_query(F.data.startswith(f"edit_{CATEGORY_FORM}:"))
async def edit_any_category_field(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer()

    field_name = callback.data.split(":")[1]
    await form_set_current_field(state, CATEGORY_FORM, field_name)

    await callback.message.edit_text(f"Введіть нові дані про {category_mapping.get(field_name)}:")
    await state.set_state(CategoryForm.waiting_input)


@router.message(CategoryForm.waiting_input)
async def process_category_input(message: types.Message, state: FSMContext, bot: Bot):
    form: TGForm = await form_get(state, CATEGORY_FORM)
    field_name = form.get("current_field")

    if not field_name:
        await finish_text_input(state, message, CATEGORY_FORM)
        await handle_message_error(message, "Упс! Оберіть поле для редагування ще раз.")
        return

    value = (message.text or "").strip()
    if not value:
        await handle_message_error(message, "❌ Значення не може бути порожнім.")
        return

    await form_set_value(state, CATEGORY_FORM, field_name, value)

    text = await render_upsert_category(state)
    await refresh_form_message(state=state, bot=bot, text=text, form_name=CATEGORY_FORM, mapping=category_mapping)

    await finish_text_input(state, message, CATEGORY_FORM)


async def render_upsert_category(state: FSMContext) -> str:
    form: TGForm = await form_get(state, CATEGORY_FORM)
    values = form["values"]

    def val(k: str) -> str:
        v = values.get(k, None)
        return str(v) if v is not None else "—"

    text = "🏷️ **Категорія**\n\n"
    text += "\n".join(f"{category_mapping.get(k).capitalize()}: {val(k)}" for k in category_mapping.keys())
    return text


@router.message(F.text == ActivityMenu.BTN_ADD_EDIT_CATEGORY)
async def show_category_upsert_form(message: types.Message, state: FSMContext):
    text = await render_upsert_category(state)

    sent_message = await message.answer(
        text,
        reply_markup=get_form_keyboard(category_mapping, CATEGORY_FORM),
        parse_mode="Markdown",
    )

    await form_set_last_msg(state=state, form_name=CATEGORY_FORM, chat_id=sent_message.chat.id, message_id=sent_message.message_id)
    await state.set_state(CategoryForm.waiting_input)
