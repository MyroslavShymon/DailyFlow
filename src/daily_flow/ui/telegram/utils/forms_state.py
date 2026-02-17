from typing import TypedDict, Any

from aiogram import types, Bot
from aiogram.fsm.context import FSMContext
from aiogram.exceptions import TelegramBadRequest, TelegramForbiddenError

from daily_flow.ui.telegram.utils.form_render import get_form_keyboard

FORMS_KEY = "forms"

class TGLastMsg(TypedDict):
    chat_id: int | None
    message_id: int | None

class TGForm(TypedDict):
    values: dict[str, Any | None]
    current_field: str | None
    last_msg: TGLastMsg

DEFAULT_FORM: TGForm = {
  "values": {},
  "current_field": None,
  "last_msg": {"chat_id": None, "message_id": None},
}

async def form_get(state: FSMContext, form_name: str) -> TGForm:
    data = await state.get_data()
    return data.get(FORMS_KEY, {}).get(form_name, DEFAULT_FORM)

async def form_patch(state: FSMContext, form_name: str, patch: dict) -> None:
    data = await state.get_data()
    forms = data.get(FORMS_KEY, {})
    form: TGForm = forms.get(form_name, {})
    form.update(patch)
    forms[form_name] = form
    await state.update_data({FORMS_KEY: forms})

async def form_set_value(state: FSMContext, form_name: str, key: str, value) -> None:
    data = await state.get_data()
    forms = data.get(FORMS_KEY, {})
    form = forms.get(form_name, {})
    values = form.get("values", {})
    values[key] = value
    form["values"] = values
    forms[form_name] = form
    await state.update_data({FORMS_KEY: forms})

async def form_set_last_msg(state: FSMContext, form_name: str, chat_id: int, message_id: int) -> None:
    await form_patch(state, form_name, {"last_msg": {"chat_id": chat_id, "message_id": message_id}})

async def form_set_current_field(state: FSMContext, form_name: str, current_filed: str | None) -> None:
    await form_patch(state, form_name, {"current_field": current_filed})

async def form_reset(state, form_name: str):
    data = await state.get_data()
    forms = data.get(FORMS_KEY, {})
    forms.pop(form_name, None)
    await state.update_data({FORMS_KEY: forms})

async def refresh_form_message(
        state: FSMContext,
        bot: Bot,
        text: str,
        form_name: str,
        mapping: dict[str, str]
) -> None:
    form: TGForm = await form_get(state, form_name)

    chat_id = form["last_msg"].get("chat_id")
    message_id = form["last_msg"].get("message_id")
    if not chat_id or not message_id:
        return

    try:
        await bot.edit_message_text(
            text=text,
            chat_id=chat_id,
            message_id=message_id,
            reply_markup=get_form_keyboard(mapping, form_name),
            parse_mode="Markdown"
        )
    except TelegramBadRequest as e:
        if "message is not modified" in str(e):
            return
        return
    except TelegramForbiddenError:
        return

async def finish_text_input(
        state: FSMContext,
        message: types.Message,
        form_name: str
):
    await message.delete()
    await form_set_current_field(state, form_name, None)
    await state.set_state(None)
