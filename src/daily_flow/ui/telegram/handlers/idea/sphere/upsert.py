import logging

from aiogram import Bot, F, types
from aiogram.fsm.context import FSMContext

from daily_flow.ui.telegram.constants.idea import sphere_mapping
from daily_flow.ui.telegram.keyboards.idea import IdeaMenu
from daily_flow.ui.telegram.runtime import router
from daily_flow.ui.telegram.states import SphereForm
from daily_flow.ui.telegram.utils.errors import handle_message_error
from daily_flow.ui.telegram.utils.form_render import get_form_keyboard
from daily_flow.ui.telegram.utils.forms_state import (
    TGForm,
    finish_text_input,
    form_get,
    form_set_current_field,
    form_set_last_msg,
    form_set_value,
    refresh_form_message,
)

logger = logging.getLogger(__name__)

SPHERE_FORM = "sphere"


@router.callback_query(F.data.startswith(f"edit_{SPHERE_FORM}:"))
async def edit_any_sphere_field(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer()

    field_name = callback.data.split(":")[1]
    await form_set_current_field(state, SPHERE_FORM, field_name)

    await callback.message.edit_text(f"Введіть нові дані про {sphere_mapping.get(field_name)}:")
    await state.set_state(SphereForm.waiting_input)


@router.message(SphereForm.waiting_input)
async def process_sphere_input(message: types.Message, state: FSMContext, bot: Bot):
    form: TGForm = await form_get(state, SPHERE_FORM)
    field_name = form.get("current_field")

    if not field_name:
        await finish_text_input(state, message, SPHERE_FORM)
        await handle_message_error(message, "Упс! Оберіть поле для редагування ще раз.")
        return

    value = (message.text or "").strip()

    if field_name == "name":
        if not value:
            await handle_message_error(message, "❌ Назва сфери (name) не може бути порожньою.")
            return
        await form_set_value(state, SPHERE_FORM, "name", value)

    elif field_name == "description":
        if not value:
            await handle_message_error(
                message, "❌ Опис не може бути порожнім рядком (або не заповнюй його)."
            )
            return
        await form_set_value(state, SPHERE_FORM, "description", value)

    else:
        await handle_message_error(message, "❌ Невідоме поле. Спробуй ще раз.")
        return

    text = await render_upsert_sphere(state)

    await refresh_form_message(
        state=state,
        bot=bot,
        text=text,
        form_name=SPHERE_FORM,
        mapping=sphere_mapping,
    )

    await finish_text_input(state, message, SPHERE_FORM)


async def render_upsert_sphere(state: FSMContext) -> str:
    form: TGForm = await form_get(state, SPHERE_FORM)

    sphere_data = {
        "name": form["values"].get("name", "—") or "—",
        "description": form["values"].get("description", "—") or "—",
    }

    text = "🧭 **Сфера**\n\n"
    text += "\n".join(f"{sphere_mapping.get(k).capitalize()}: {v}" for k, v in sphere_data.items())

    return text


@router.message(F.text == IdeaMenu.BTN_ADD_EDIT_SPHERE)
async def show_sphere_upsert_form(message: types.Message, state: FSMContext):
    text = await render_upsert_sphere(state)

    sent_message = await message.answer(
        text,
        reply_markup=get_form_keyboard(sphere_mapping, SPHERE_FORM),
        parse_mode="Markdown",
    )

    await form_set_last_msg(
        state=state,
        form_name=SPHERE_FORM,
        chat_id=sent_message.chat.id,
        message_id=sent_message.message_id,
    )

    await state.set_state(SphereForm.waiting_input)
