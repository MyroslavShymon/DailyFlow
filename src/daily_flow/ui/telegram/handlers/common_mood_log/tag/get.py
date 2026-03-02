import logging
from datetime import datetime

from aiogram import F, types
from aiogram.fsm.context import FSMContext

from daily_flow.app.container import Container
from daily_flow.ui.telegram.keyboards.common_mood import CommonMoodMenu
from daily_flow.ui.telegram.render.сommon_mood_log import render_tag_impact
from daily_flow.ui.telegram.runtime import router
from daily_flow.ui.telegram.states import TagImpactGetForm
from daily_flow.ui.telegram.utils.cache_state import get_cache, set_cache_field
from daily_flow.ui.telegram.utils.date_selection import DateAction, get_date_keyboard

logger = logging.getLogger(__name__)


async def get_all_tags(state: FSMContext, db_container: Container) -> list[str]:
    cache = await get_cache(state)
    tags = cache.get("tags")

    if not tags:
        tags = await db_container.common_mood_log_service.get_all_unique_tags()
        await set_cache_field(state, "tags", tags)

    return tags


async def get_all_tags_text(state: FSMContext, db_container: Container) -> str:
    tags = await get_all_tags(state, db_container)

    if not tags:
        return "На жаль, поки немає тегів"

    tags_list = "\n".join([f"• {tag}" for tag in tags])
    text = (
        "📊 **Ваші наявні чинники впливу**\n\n"
        "Ось список тегів, які ви використовували раніше для аналізу настрою:\n\n"
        f"{tags_list}\n\n"
        "💡 _Ви можете обрати один із них або додати новий._"
    )

    return text


@router.message(F.text == CommonMoodMenu.BTN_GET_ALL_TAGS)
async def get_all_tag_impacts(message: types.Message, state: FSMContext, db_container: Container):
    text = await get_all_tags_text(state, db_container)
    await message.answer(text)


async def perform_tag_impact_get(
    message: types.Message, date_str: str, state: FSMContext, db_container: Container
):
    try:
        selected_date = datetime.strptime(date_str, "%d-%m-%Y").date()
        tags_by_day = await db_container.common_mood_log_service.get_tags_by_day(selected_date)

        await state.clear()

        if not tags_by_day:
            await message.answer(
                f"🔍 Схоже, за {date_str} ще немає жодного запису.",
                reply_markup=CommonMoodMenu.get(),
            )
        else:
            tags_by_day_text = "\n".join(render_tag_impact(t, date_str) for t in tags_by_day)
            await message.answer(
                "🔍 Ось результат пошуку: \n" + tags_by_day_text, reply_markup=CommonMoodMenu.get()
            )

    except ValueError:
        await message.answer("❌ Невірний формат. Спробуй ще раз (наприклад: 25-12-2006):")
    except Exception as e:
        logger.error("Service error: %s", e)
        await message.answer("❌ Сталася помилка сервісу.")


@router.message(F.text == CommonMoodMenu.BTN_GET_TAGS_BY_DAY)
async def get_tag_impact(message: types.Message, state: FSMContext):
    await state.set_state(TagImpactGetForm.waiting_for_date)
    await message.answer(
        "Будь ласка, обери дату для запису, який треба переглянути:",
        reply_markup=get_date_keyboard(DateAction.GET, "tag_impact"),
        parse_mode="Markdown",
    )
