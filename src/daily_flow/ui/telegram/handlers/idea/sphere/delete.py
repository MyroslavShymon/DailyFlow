import asyncio
import logging

from aiogram import types, F
from aiogram.fsm.context import FSMContext

from daily_flow.ui.telegram.keyboards.idea import IdeaMenu
from daily_flow.ui.telegram.runtime import c, router
from daily_flow.ui.telegram.states import SphereDeleteForm
from daily_flow.ui.telegram.handlers.idea.sphere.get import get_all_spheres_text

logger = logging.getLogger(__name__)

@router.message(F.text == IdeaMenu.BTN_DELETE_SPHERE)
async def delete_sphere(message: types.Message, state: FSMContext):
    await state.set_state(SphereDeleteForm.waiting_for_name)

    spheres_text = await get_all_spheres_text()

    await message.answer(
        "Введи точну назву (name) сфери, яку треба видалити."
        f"{spheres_text}",
        reply_markup=IdeaMenu.get(),
        parse_mode="Markdown",
    )


@router.message(SphereDeleteForm.waiting_for_name)
async def perform_delete_sphere(message: types.Message, state: FSMContext):
    name = (message.text or "").strip()

    if not name:
        return await message.answer("❌ Name не може бути порожнім. Введи name ще раз:")

    try:
        deleted = await asyncio.to_thread(c.idea_service.delete_sphere_by_name, name)
        await state.clear()

        if deleted > 0:
            await message.answer("✅ Сферу видалено.", reply_markup=IdeaMenu.get())
        else:
            await message.answer("🔍 Сферу з таким name не знайдено (або вже була видалена).", reply_markup=IdeaMenu.get())

    except Exception as e:
        logger.exception("Sphere delete_sphere_by_name failed: %s", e)
        await state.clear()
        await message.answer("❌ Сталася помилка під час видалення сфери.", reply_markup=IdeaMenu.get())
