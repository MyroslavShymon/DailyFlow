import logging
from datetime import datetime

from aiogram import types, F
from aiogram.fsm.context import FSMContext

from daily_flow.ui.telegram.keyboards.common_mood import CommonMoodMenu
from daily_flow.ui.telegram.runtime import router, c
from daily_flow.ui.telegram.states import TagImpactDeleteForm
from daily_flow.ui.telegram.utils.date_selection import get_date_keyboard, DateAction


logger = logging.getLogger(__name__)

async def perform_tag_impact_delete(
        message: types.Message,
        state: FSMContext,
        date_str: str,
        tag: str | None
):
    try:
        selected_date = datetime.strptime(date_str, "%d-%m-%Y").date()
        tag_impact = c.common_mood_log_service.get_tags_by_day(selected_date)

        if not tag_impact:
            await state.clear()
            return await message.answer(
                f"🔍 Схоже, за {date_str} ще немає жодного запису. Видаляти нічого!",
                reply_markup=CommonMoodMenu.get()
            )

        if not tag:
            await state.clear()
            return await message.answer(
                f"🔍 Схоже, з чинником {tag} ще немає жодного запису. Видаляти нічого!",
                reply_markup=CommonMoodMenu.get()
            )

        deleted_count = c.common_mood_log_service.delete_tag_by_day(
            day=selected_date,
            tag=tag
        )

        if deleted_count > 0:
            await state.clear()
            await message.answer(
                "✅ Дані видалено! Повертаємось у меню настрою:",
                reply_markup=CommonMoodMenu.get()
            )
        elif deleted_count == 0:
            await message.answer(
                f"🔍 Схоже, з чинником {tag} ще немає жодного запису або видалення не відбулось з інших причин",
                reply_markup=CommonMoodMenu.get()
            )
    except ValueError:
        await message.answer("❌ Невірний формат. Спробуй ще раз (наприклад: 25-12-2006):")
    except Exception as e:
        logger.error("Service error: %s", e)
        await message.answer(f"❌ Сталася помилка сервісу.")

@router.message(F.text == CommonMoodMenu.BTN_DELETE_TAG_BY_DAY)
async def delete_tag_impact(message: types.Message, state: FSMContext):
    await state.set_state(TagImpactDeleteForm.waiting_for_tag_name)
    await message.answer("Будь ласка, введи тег, який треба видалити:")

@router.message(TagImpactDeleteForm.waiting_for_tag_name)
async def delete_tag_impact(message: types.Message, state: FSMContext):
    tag_to_delete = message.text.strip()
    await state.set_state(TagImpactDeleteForm.waiting_for_date)
    await message.answer(
        "Будь ласка, обери дату для запису, який треба видалити:",
        reply_markup=get_date_keyboard(
            DateAction.DELETE,
            "tag_impact",
            optional_fields={"tag": tag_to_delete}
        ),
        parse_mode="Markdown"
    )
