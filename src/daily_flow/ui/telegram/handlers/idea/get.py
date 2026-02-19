import asyncio
import logging

from aiogram import types, F
from aiogram.fsm.context import FSMContext

from daily_flow.ui.telegram.keyboards.idea import IdeaMenu
from daily_flow.ui.telegram.render.idea import render_idea
from daily_flow.ui.telegram.runtime import c, router
from daily_flow.ui.telegram.states import IdeaBySphereGetForm
from daily_flow.ui.telegram.handlers.idea.sphere.get import get_all_spheres_text


logger = logging.getLogger(__name__)

async def get_all_ideas_text() -> str:
    ideas = await asyncio.to_thread(c.idea_service.get_all_ideas)

    if not ideas:
        return "💡 Поки що немає жодної ідеї.\n\nСтвори першу через «✨ Додати/оновити ідею»."

    ideas_text = "\n".join(render_idea(i) for i in ideas)

    text = "💡 **Список ідей**:\n" + ideas_text
    if len(text) > 3500:
        text = text[:3500] + "\n…"
    return text


@router.message(F.text == IdeaMenu.BTN_GET_ALL_IDEAS)
async def get_all_ideas(message: types.Message):
    try:
        text = await get_all_ideas_text()
        await message.answer(text, reply_markup=IdeaMenu.get(), parse_mode="Markdown")
    except Exception as e:
        logger.exception("Idea get_all_ideas failed: %s", e)
        await message.answer("❌ Сталася помилка під час отримання списку ідей.", reply_markup=IdeaMenu.get())


@router.message(F.text == IdeaMenu.BTN_IDEAS_BY_SPHERE)
async def ask_sphere_id_for_ideas(message: types.Message, state: FSMContext):
    await state.set_state(IdeaBySphereGetForm.waiting_for_sphere_id)

    spheres_text = await get_all_spheres_text()

    await message.answer(
        "Введи **ID сфери**, щоб показати ідеї в ній.\n\n"
        f"{spheres_text}",
        reply_markup=IdeaMenu.get(),
        parse_mode="Markdown",
    )


@router.message(IdeaBySphereGetForm.waiting_for_sphere_id)
async def show_ideas_by_sphere(message: types.Message, state: FSMContext):
    raw = (message.text or "").strip()

    try:
        sphere_id = int(raw)
    except ValueError:
        return await message.answer("❌ ID сфери має бути числом. Спробуй ще раз:")

    try:
        ideas = await asyncio.to_thread(c.idea_service.get_ideas_by_sphere, sphere_id)

        await state.clear()

        if not ideas:
            return await message.answer(
                f"📌 За сферою ID={sphere_id} ідей поки немає.",
                reply_markup=IdeaMenu.get(),
            )

        ideas_text = "\n".join(render_idea(i) for i in ideas)

        text = (
            f"📌 **Ідеї за сферою ID={sphere_id}**\n\n"
            + ideas_text
        )
        await message.answer(text, reply_markup=IdeaMenu.get(), parse_mode="Markdown")

    except Exception as e:
        logger.exception("Idea get_ideas_by_sphere failed: %s", e)
        await state.clear()
        await message.answer("❌ Сталася помилка під час отримання ідей за сферою.", reply_markup=IdeaMenu.get())
