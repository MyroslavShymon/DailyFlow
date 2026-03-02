import logging

from aiogram import Bot, F, types
from aiogram.fsm.context import FSMContext

from daily_flow.ui.telegram.constants.common_mood_log import common_mood_log_mapping
from daily_flow.ui.telegram.keyboards.common_mood import CommonMoodMenu
from daily_flow.ui.telegram.runtime import router
from daily_flow.ui.telegram.states import CommonMoodLogForm
from daily_flow.ui.telegram.utils.date_parse import parse_to_date
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
from daily_flow.ui.telegram.utils.keyboard import build_inline_keyboard

logger = logging.getLogger(__name__)

COMMON_MOOD_LOG_FORM = "common_mood_log"


@router.callback_query(F.data.startswith(f"edit_{COMMON_MOOD_LOG_FORM}:"))
async def edit_any_common_mood_field(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer()

    field_name = callback.data.split(":")[1]
    await form_set_current_field(state, COMMON_MOOD_LOG_FORM, field_name)

    moods = ["😢 1", "☹️ 2", "😐 3", "🙂 4", "😊 5", "😁 6", "🤩 7"]
    moods_start_index = 1
    moods_button_adjust = [4, 3]
    moods_field_name = "mood"

    if field_name == "mood":
        await callback.message.edit_text(
            "Оберіть ваш рівень настрою:",
            reply_markup=build_inline_keyboard(
                field_name=moods_field_name,
                button_names=moods,
                start_index=moods_start_index,
                button_adjusts=moods_button_adjust,
            ),
        )
    else:
        await callback.message.edit_text(
            f"Введіть ваші нові дані про {common_mood_log_mapping.get(field_name)}:"
        )
        await state.set_state(CommonMoodLogForm.waiting_input)


@router.callback_query(F.data.startswith("set_mood_value:"))
async def process_mood_selection(callback: types.CallbackQuery, state: FSMContext, bot: Bot):
    await callback.answer()
    mood_value = int(callback.data.split(":")[1])

    await form_set_value(state, COMMON_MOOD_LOG_FORM, "mood", mood_value)
    await form_set_current_field(state, COMMON_MOOD_LOG_FORM, None)

    text = await render_upsert_common_mood(state)

    await refresh_form_message(
        text=text,
        state=state,
        bot=bot,
        form_name=COMMON_MOOD_LOG_FORM,
        mapping=common_mood_log_mapping,
    )

    await callback.answer(f"Настрій {mood_value} збережено!")


@router.message(CommonMoodLogForm.waiting_input)
async def process_common_mood_input(message: types.Message, state: FSMContext, bot: Bot):
    form: TGForm = await form_get(state, COMMON_MOOD_LOG_FORM)
    field_name = form.get("current_field")

    if not field_name:
        await finish_text_input(state, message, COMMON_MOOD_LOG_FORM)
        await handle_message_error(message, "Упс! Оберіть поле для редагування ще раз.")
        return

    if field_name == "day":
        valid_date = parse_to_date(message.text)
        if not valid_date:
            await handle_message_error(message, "Помилка: Рядок не відповідає формату DD-MM-YYYY")
            return
        await form_set_value(state, COMMON_MOOD_LOG_FORM, "day", valid_date)
    elif field_name == "note":
        await form_set_value(state, COMMON_MOOD_LOG_FORM, "note", message.text)

    text = await render_upsert_common_mood(state)

    await refresh_form_message(
        text=text,
        state=state,
        bot=bot,
        form_name=COMMON_MOOD_LOG_FORM,
        mapping=common_mood_log_mapping,
    )

    await finish_text_input(state, message, COMMON_MOOD_LOG_FORM)


async def render_upsert_common_mood(state: FSMContext) -> str:
    form: TGForm = await form_get(state, COMMON_MOOD_LOG_FORM)

    common_mood_data = {
        mood: form["values"].get(mood, "—") for mood in common_mood_log_mapping.keys()
    }

    text = (
        f"📋 **Запис про настрій за {common_mood_data.get('day')}**\n\n"
        if common_mood_data.get("day") != "—"
        else "Запис про настрій за не вказаний день\n"
    )
    text += "\n".join(
        f"{common_mood_log_mapping.get(k).capitalize()}: {v}" for k, v in common_mood_data.items()
    )

    return text


@router.message(F.text == CommonMoodMenu.BTN_ADD_EDIT_COMMON_MOOD_LOG)
async def show_common_mood_upsert_data(message: types.Message, state: FSMContext):
    text = await render_upsert_common_mood(state)

    sent_message = await message.answer(
        text,
        reply_markup=get_form_keyboard(common_mood_log_mapping, COMMON_MOOD_LOG_FORM),
        parse_mode="Markdown",
    )

    await form_set_last_msg(
        state=state,
        form_name=COMMON_MOOD_LOG_FORM,
        chat_id=sent_message.chat.id,
        message_id=sent_message.message_id,
    )

    await state.set_state(CommonMoodLogForm.waiting_input)
