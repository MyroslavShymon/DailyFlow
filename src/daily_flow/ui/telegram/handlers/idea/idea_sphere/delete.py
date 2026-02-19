import asyncio
import logging

from aiogram import types, F
from aiogram.fsm.context import FSMContext

from daily_flow.services.idea.dto import SphereToIdeaDTO
from daily_flow.ui.telegram.handlers.idea.get import get_all_ideas_text
from daily_flow.ui.telegram.handlers.idea.sphere.get import get_all_spheres_text
from daily_flow.ui.telegram.keyboards.idea import IdeaMenu
from daily_flow.ui.telegram.runtime import c, router
from daily_flow.ui.telegram.states import SphereToIdeaDeleteForm

logger = logging.getLogger(__name__)

KEY_IDEA_ID = "idea_id_for_delete"


@router.message(F.text == IdeaMenu.BTN_DELETE_SPHERE_FROM_IDEA)
async def delete_sphere_from_idea(message: types.Message, state: FSMContext):
    await state.set_state(SphereToIdeaDeleteForm.waiting_for_idea_id)

    ideas_text = await get_all_ideas_text()

    await message.answer(
        "Введи **ID ідеї**, з якої треба прибрати сферу:\n\n"
        f"{ideas_text}",
        reply_markup=IdeaMenu.get(),
        parse_mode="Markdown",
    )


@router.message(SphereToIdeaDeleteForm.waiting_for_idea_id)
async def delete_sphere_from_idea_step1(message: types.Message, state: FSMContext):
    raw = (message.text or "").strip()

    try:
        idea_id = int(raw)
    except ValueError:
        return await message.answer("❌ ID ідеї має бути числом. Спробуй ще раз:")

    await state.update_data({KEY_IDEA_ID: idea_id})
    await state.set_state(SphereToIdeaDeleteForm.waiting_for_sphere_id)

    spheres_text = await get_all_spheres_text()

    await message.answer(
        "Тепер введи **ID сфери**, яку треба прибрати з цієї ідеї:\n\n"
        f"{spheres_text}",
        reply_markup=IdeaMenu.get(),
        parse_mode="Markdown",
    )


@router.message(SphereToIdeaDeleteForm.waiting_for_sphere_id)
async def delete_sphere_from_idea_step2(message: types.Message, state: FSMContext):
    data = await state.get_data()
    idea_id = data.get(KEY_IDEA_ID)

    raw = (message.text or "").strip()

    try:
        sphere_id = int(raw)
    except ValueError:
        return await message.answer("❌ ID сфери має бути числом. Спробуй ще раз:")

    try:
        dto = SphereToIdeaDTO(sphere_id=sphere_id, idea_id=idea_id)
        deleted_count = await asyncio.to_thread(c.idea_service.delete_sphere_from_idea, dto)

        await state.clear()

        if deleted_count > 0:
            await message.answer("✅ Сферу прибрано з ідеї!", reply_markup=IdeaMenu.get())
        else:
            await message.answer(
                "🔍 Нічого не видалено (звʼязок не знайдено).",
                reply_markup=IdeaMenu.get()
            )

    except Exception as e:
        logger.exception("Idea delete_sphere_from_idea failed: %s", e)
        await state.clear()
        await message.answer("❌ Сталася помилка під час видалення звʼязку.", reply_markup=IdeaMenu.get())
