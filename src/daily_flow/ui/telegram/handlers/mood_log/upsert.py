import logging
from datetime import datetime, timedelta

from aiogram import types, F

from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.fsm.context import FSMContext

from pydantic import ValidationError

from daily_flow.ui.telegram.keyboards.main import MainMenu
from daily_flow.ui.telegram.keyboards.mood import MoodMenu
from daily_flow.ui.telegram.render.mood_log import render_mood_log
from daily_flow.ui.telegram.runtime import router, dp, c
from daily_flow.ui.telegram.states import MoodLogForm
from daily_flow.services.errors import ServiceError
from daily_flow.services.mood_log.dto import UpsertMoodLogDTO
from daily_flow.ui.telegram.constants.mood_log import mood_log_mapping


logger = logging.getLogger(__name__)

def get_form_keyboard():
    builder = InlineKeyboardBuilder()
    for mood, mood_translated in mood_log_mapping.items():
        builder.row(types.InlineKeyboardButton(text=f"Введіть дані про {mood_translated}", callback_data=f"edit_mood_{mood}"))
    builder.row(types.InlineKeyboardButton(text="✅ Все вірно", callback_data="submit_mood_log_form"))
    return builder.as_markup()

@router.callback_query(F.data == "submit_mood_log_form")
async def submit_mood_log_form(callback: types.CallbackQuery, state: FSMContext):
    print(f"submit_mood_log_form")
    data = await state.get_data()
    print(f"ffffffffsadfdsfgsdfg{data=}")

    try:
        day = data.pop("day")
        # day_str = data.pop("day")
        # day = datetime.strptime(day_str, "%d-%m-%Y").date()
        # print(f"sdfgfghfgngf{day=}")
        vals = {mood: data.get(mood) for mood in mood_log_mapping.keys() if mood != "day"}
        print(f"sdfnhjk546{vals=}")
        dto = UpsertMoodLogDTO(
            day=day,
            **vals
        )

        saved = c.mood_log_service.upsert_mood_log(dto)
        if saved:
            await callback.message.answer(f"{render_mood_log(saved)}")
            await state.set_data({})
            await callback.message.answer(
                "✅ Дані збережено! Повертаємось у головне меню:",
                reply_markup=MainMenu.get()
            )
        # print("SAVED:", saved)
    except ValidationError as e:
        # Беремо першу помилку і робимо її людяною
        err = e.errors()[0]
        field = err['loc'][0]
        msg = err['msg']

        # Свій переклад або обробка
        friendly_msg = f"Значення поля '{field}' некоректне: {msg}"
        await callback.message.answer(f"❌ {friendly_msg}")
    except (ServiceError, ValueError) as e:
        logger.error("Service error: %s", e)
        error_text = str(e)
        await callback.message.answer(f"❌ Помилка: {error_text}")


@router.callback_query(F.data.startswith("edit_mood_"))
async def edit_any_mood_field(callback: types.CallbackQuery, state: FSMContext):
    print(f"edit_any_mood_field")
    field_name = callback.data[10:]
    print(f"{field_name=}")
    await callback.message.edit_text(f"Введіть ваші нові дані про {mood_log_mapping.get(field_name)}:")
    await state.update_data(current_editing_field=field_name)
    await state.set_state(MoodLogForm.waiting_for_any_mood_log_input)
    await callback.answer()

@router.message(F.text == MoodMenu.BTN_ADD_EDIT_MOOD_LOG)
async def show_mood_upsert_data(message: types.Message, state: FSMContext):
    print(f"show_mood_upsert_data")
    data = await state.get_data()
    print(f'{data=}')

    mood_data = {mood: data.get(mood, "—") for mood in mood_log_mapping.keys()}

    day = mood_data.get('day')
    day_text = f"📋 **Запис про емоції за {day}**\n\n" if day != "—" else "Запис про настрій за не вказаний день\n"

    moods_text = "\n".join(f'{mood_log_mapping.get(k).capitalize()}: {v}' for k ,v in mood_data.items())

    text = day_text + moods_text
    print(f"{text=}")
    await message.answer(text, reply_markup=get_form_keyboard(), parse_mode="Markdown")


@router.message(MoodLogForm.waiting_for_any_mood_log_input)
async def process_mood_input(message: types.Message, state: FSMContext):
    print(f"process_mood_input")
    if message.text.startswith("📝") or message.text.startswith("💡") or message.text.startswith("/"):
        await state.clear()
        return await dp.propagate_event(message)

    data = await state.get_data()
    field_name = data.get("current_editing_field")

    if not field_name:
        await message.delete()
        await state.set_state(None)
        return await message.answer("Упс! Оберіть поле для редагування ще раз.", reply_markup=get_form_keyboard())

    if field_name == "day":
        try:
            valid_date = datetime.strptime(message.text, "%d-%m-%Y").date()

            await message.answer(f"Дані по полю {mood_log_mapping[field_name]} записані оберіть інше поле")
            await state.update_data({"day": valid_date})
            await state.set_state(None)
        except ValueError:
            await message.answer("Помилка: Рядок не відповідає формату DD-MM-YYYY")
    else:
        try:
            mood = int(message.text)
            if not 0 < mood < 5:
                return await message.answer("Будь ласка, введіть число від 1 до 4 (де 1 — мінімум, 4 — максимум).")

            await message.answer(f"Дані по полю {mood_log_mapping[field_name]} записані оберіть інше поле")
            await state.update_data({field_name: mood})
            await state.set_state(None)
        except ValueError as e:
            await message.answer(str(e) or "Ой! Це не схоже на ціле число")

    await state.update_data(current_editing_field=None)
    await state.set_state(None)

    await show_mood_upsert_data(message, state)

