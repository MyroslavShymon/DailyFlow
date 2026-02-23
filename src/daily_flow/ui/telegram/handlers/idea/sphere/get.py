import asyncio
import logging

from aiogram import types, F

from daily_flow.app.container import Container
from daily_flow.ui.telegram.keyboards.idea import IdeaMenu
from daily_flow.ui.telegram.render.idea import render_sphere
from daily_flow.ui.telegram.runtime import router


logger = logging.getLogger(__name__)

async def get_all_spheres_text(db_container: Container) -> str:
    spheres = await db_container.idea_service.get_all_spheres()

    if not spheres:
        return "🗂️ **Сфери**\n\nПоки що жодної сфери немає."

    spheres_text = "\n".join(render_sphere(s) for s in spheres)

    return "🗂️ **Сфери**:\n" + spheres_text


@router.message(F.text == IdeaMenu.BTN_GET_ALL_SPHERES)
async def get_all_spheres(message: types.Message, db_container: Container):
    try:
        text = await get_all_spheres_text(db_container)
        await message.answer(text, reply_markup=IdeaMenu.get(), parse_mode="Markdown")
    except Exception as e:
        logger.exception("Sphere get_all_spheres failed: %s", e)
        await message.answer("❌ Сталася помилка під час отримання сфер.", reply_markup=IdeaMenu.get())
