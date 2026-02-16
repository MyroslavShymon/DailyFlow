import asyncio
import logging
from datetime import datetime

from aiogram import types, F, Bot
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import InlineKeyboardBuilder
from pydantic_core._pydantic_core import ValidationError

from daily_flow.services.common_mood.dto import UpsertCommonMoodLogDTO
from daily_flow.services.errors import ServiceError
from daily_flow.ui.telegram.constants.common_mood_log import common_mood_log_mapping
from daily_flow.ui.telegram.keyboards.common_mood import CommonMoodMenu
from daily_flow.ui.telegram.keyboards.main import MainMenu
from daily_flow.ui.telegram.runtime import router, c
from daily_flow.ui.telegram.states import CommonMoodLogForm
from daily_flow.ui.telegram.utils.errors import handle_message_error
from daily_flow.ui.telegram.utils.form_render import get_form_keyboard
from daily_flow.ui.telegram.render.сommon_mood_log import render_common_mood_log

logger = logging.getLogger(__name__)

def get_mood_scale_keyboard():
    builder = InlineKeyboardBuilder()
    moods = ["😢 1", "☹️ 2", "😐 3", "🙂 4", "😊 5", "😁 6", "🤩 7"]

    for i, label in enumerate(moods, start=1):
        builder.button(text=label, callback_data=f"set_mood_value:{i}")

    builder.adjust(4, 3)
    return builder.as_markup()

@router.callback_query(F.data == "submit_common_mood_log_form")
async def submit_common_mood_log_form(
        callback: types.CallbackQuery,
        state: FSMContext,
        bot: Bot
):
    await callback.answer()

    data = await state.get_data()

    last_chat_id = data.get("last_chat_id")
    last_form_message_id = data.get("last_form_message_id")

    try:
        dto = UpsertCommonMoodLogDTO(
            day=data.get("day"),
            mood=data.get("mood"),
            note=data.get("note"),
        )
        saved = await asyncio.to_thread(c.common_mood_log_service.upsert_common_mood_log, dto)
        if saved:
            await bot.delete_message(
                chat_id=last_chat_id,
                message_id=last_form_message_id
            )
            await callback.message.answer(f"{render_common_mood_log(saved)}")
            await state.set_data({})
            await callback.message.answer(
                "✅ Дані збережено! Повертаємось у головне меню:",
                reply_markup=MainMenu.get()
            )
    except ValidationError as e:
        err = e.errors()[0]
        field = err['loc'][0]
        msg = err['msg']

        friendly_msg = f"Значення поля '{field}' некоректне: {msg}"
        await callback.message.answer(f"❌ {friendly_msg}")
    except (ServiceError, ValueError) as e:
        logger.error("Service error: %s", e)
        error_text = str(e)
        await callback.message.answer(f"❌ Помилка: {error_text}")


@router.callback_query(F.data.startswith("edit_common_mood_log_"))
async def edit_any_common_mood_field(callback: types.CallbackQuery, state: FSMContext):
    field_name = callback.data[21:]
    await state.update_data(current_editing_field=field_name)

    if field_name == "mood":
        await callback.message.edit_text(
            "Оберіть ваш рівень настрою:",
            reply_markup=get_mood_scale_keyboard()
        )
    else:
        await callback.message.edit_text(f"Введіть ваші нові дані про {common_mood_log_mapping.get(field_name)}:")
        await state.set_state(CommonMoodLogForm.waiting_for_any_common_mood_input)

    await callback.answer()


@router.callback_query(F.data.startswith("set_mood_value:"))
async def process_mood_selection(callback: types.CallbackQuery, state: FSMContext, bot: Bot):
    await callback.answer()
    mood_value = callback.data.split(":")[1]

    await state.update_data(mood=mood_value, current_editing_field=None)

    data = await state.get_data()
    text = await render_upsert_common_mood(state)

    await bot.edit_message_text(
        text=text,
        chat_id=callback.message.chat.id,
        message_id=data.get("last_form_message_id"),
        reply_markup=get_form_keyboard(common_mood_log_mapping, 'common_mood_log'),
        parse_mode="Markdown"
    )
    await callback.answer(f"Настрій {mood_value} збережено!")

@router.message(CommonMoodLogForm.waiting_for_any_common_mood_input)
async def process_common_mood_input(
        message: types.Message,
        state: FSMContext,
        bot: Bot
):
    data = await state.get_data()
    field_name = data.get("current_editing_field")
    last_chat_id = data.get("last_chat_id")
    last_form_message_id = data.get("last_form_message_id")

    if not field_name:
        await message.delete()
        await state.set_state(None)
        await handle_message_error(message, "Упс! Оберіть поле для редагування ще раз.")

    if field_name == "day":
        try:
            valid_date = datetime.strptime(message.text, "%d-%m-%Y").date()
            # await message.answer(f"Дані {message.text} по полю {common_mood_log_mapping[field_name]} записані, оберіть інше поле")
            await state.update_data({"day": valid_date})
            await state.set_state(None)
        except ValueError:
            await handle_message_error(message, "Помилка: Рядок не відповідає формату DD-MM-YYYY")

    elif field_name == "note":
        await state.update_data({"note": message.text})
        await state.set_state(None)

    text = await render_upsert_common_mood(state)
    await bot.edit_message_text(
        text=text,
        chat_id=last_chat_id,
        message_id=last_form_message_id,
        reply_markup=get_form_keyboard(common_mood_log_mapping, 'common_mood_log'),
        parse_mode="Markdown"
    )

    await message.delete()

    await state.update_data(current_editing_field=None)
    await state.set_state(None)


async def render_upsert_common_mood(state: FSMContext) -> str:
    data = await state.get_data()
    print(f"render_upsert_common_mood{data=}")
    common_mood_data = {mood: data.get(mood, "—") for mood in common_mood_log_mapping.keys()}

    text = f"📋 **Запис про настрій за {common_mood_data.get('day')}**\n\n" if common_mood_data.get('day') != "—" else "Запис про настрій за не вказаний день\n"
    text += "\n".join(f'{common_mood_log_mapping.get(k).capitalize()}: {v}' for k ,v in common_mood_data.items())

    return text

@router.message(F.text == CommonMoodMenu.BTN_ADD_EDIT_COMMON_MOOD_LOG)
async def show_common_mood_upsert_data(message: types.Message, state: FSMContext):
    print(f"show_common_mood_upsert_data")

    text = await render_upsert_common_mood(state)

    sent_message = await message.answer(text, reply_markup=get_form_keyboard(common_mood_log_mapping, 'common_mood_log'), parse_mode="Markdown")

    await state.update_data(
        last_form_message_id=sent_message.message_id,
        last_chat_id=sent_message.chat.id
    )

    await state.set_state(CommonMoodLogForm.waiting_for_any_common_mood_input)