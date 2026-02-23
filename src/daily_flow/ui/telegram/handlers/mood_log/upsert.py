import logging

from aiogram import types, F, Bot

from aiogram.fsm.context import FSMContext

from daily_flow.ui.telegram.keyboards.mood import MoodMenu
from daily_flow.ui.telegram.runtime import router
from daily_flow.ui.telegram.states import MoodLogForm
from daily_flow.ui.telegram.constants.mood_log import mood_log_mapping
from daily_flow.ui.telegram.utils.date_parse import parse_to_date
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

MOOD_LOG_FORM = "mood_log"

@router.callback_query(F.data.startswith(f"edit_{MOOD_LOG_FORM}:"))
async def edit_any_mood_log_field(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer()
    field_name = callback.data.split(":")[1]

    await form_set_current_field(state, MOOD_LOG_FORM, field_name)

    await callback.message.edit_text(f"Введіть ваші нові дані про {mood_log_mapping.get(field_name)}:")
    await state.set_state(MoodLogForm.waiting_input)

@router.message(MoodLogForm.waiting_input)
async def process_mood_input(
        message: types.Message,
        state: FSMContext,
        bot: Bot
):
    form: TGForm = await form_get(state, MOOD_LOG_FORM)
    field_name = form.get("current_field")


    if not field_name:
        await finish_text_input(state, message, MOOD_LOG_FORM)
        await handle_message_error(message, "Упс! Оберіть поле для редагування ще раз.")
        return

    if field_name == "day":
        valid_date = parse_to_date(message.text)
        if not valid_date:
            await handle_message_error(message, "Помилка: Рядок не відповідає формату DD-MM-YYYY")
            return
        await form_set_value(state, MOOD_LOG_FORM, "day", valid_date)
    else:
        try:
            mood = int(message.text)
            if not 1 <= mood <= 4:
                return await message.answer("Будь ласка, введіть число від 1 до 4 (де 1 — мінімум, 4 — максимум).")

            await form_set_value(state, MOOD_LOG_FORM, field_name, mood)
        except ValueError as e:
            await message.answer(str(e) or "Ой! Це не схоже на ціле число")
            return

    text = await render_upsert_mood(state)

    await refresh_form_message(
        text=text,
        state=state,
        bot=bot,
        form_name=MOOD_LOG_FORM,
        mapping=mood_log_mapping
    )

    await finish_text_input(state, message, MOOD_LOG_FORM)

async def render_upsert_mood(state: FSMContext) -> str:
    form: TGForm = await form_get(state, MOOD_LOG_FORM)
    mood_data = {mood: form["values"].get(mood, "—") for mood in mood_log_mapping.keys()}

    day = mood_data.get('day')
    text = f"📋 **Запис про емоції за {day}**\n\n" if day != "—" else "Запис про настрій за не вказаний день\n"
    text += "\n".join(f'{mood_log_mapping.get(k).capitalize()}: {v}' for k ,v in mood_data.items())

    return text

@router.message(F.text == MoodMenu.BTN_ADD_EDIT_MOOD_LOG)
async def show_mood_upsert_data(message: types.Message, state: FSMContext):
    text = await render_upsert_mood(state)

    sent_message = await message.answer(text, reply_markup=get_form_keyboard(mood_log_mapping, MOOD_LOG_FORM), parse_mode="Markdown")

    await form_set_last_msg(
        state=state,
        form_name=MOOD_LOG_FORM,
        chat_id=sent_message.chat.id,
        message_id=sent_message.message_id
    )

    await state.set_state(MoodLogForm.waiting_input)