import asyncio
import logging

from aiogram import types, F

from daily_flow.ui.telegram.keyboards.activity import ActivityMenu
from daily_flow.ui.telegram.render.activity import render_category_compact
from daily_flow.ui.telegram.runtime import c, router
from daily_flow.ui.telegram.utils.truncate_text import truncate_text


logger = logging.getLogger(__name__)

async def get_all_categories_text() -> str:
    categories = await asyncio.to_thread(c.category_service.get_all_categories)

    if not categories:
        return "🏷️ Поки що немає жодної категорії."

    lines = "\n".join(render_category_compact(cat) for cat in categories)
    text = "🏷️ **Список категорій**\n\n" + lines
    return truncate_text(text)


@router.message(F.text == ActivityMenu.BTN_GET_ALL_CATEGORIES)
async def get_all_categories(message: types.Message):
    try:
        text = await get_all_categories_text()
        await message.answer(text, reply_markup=ActivityMenu.get(), parse_mode="Markdown")
    except Exception as e:
        logger.exception("Category get_all_categories failed: %s", e)
        await message.answer("❌ Сталася помилка під час отримання списку категорій.", reply_markup=ActivityMenu.get())
