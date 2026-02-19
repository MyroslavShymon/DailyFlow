import asyncio
import logging

from aiogram import types, F
from aiogram.fsm.context import FSMContext

from daily_flow.services.idea.dto import SphereToIdeaDTO
from daily_flow.ui.telegram.handlers.idea.get import get_all_ideas_text
from daily_flow.ui.telegram.handlers.idea.sphere.get import get_all_spheres_text
from daily_flow.ui.telegram.keyboards.idea import IdeaMenu
from daily_flow.ui.telegram.runtime import c, router
from daily_flow.ui.telegram.states import SphereToIdeaAssignForm

logger = logging.getLogger(__name__)

KEY_IDEA_ID = "idea_id_for_assign"


@router.message(F.text == IdeaMenu.BTN_ASSIGN_SPHERE_TO_IDEA)
async def assign_sphere_to_idea(message: types.Message, state: FSMContext):
    await state.set_state(SphereToIdeaAssignForm.waiting_for_idea_id)

    ideas_text = await get_all_ideas_text()

    await message.answer(
        "Введи **ID ідеї**, до якої треба додати сферу:\n\n"
        f"{ideas_text}",
        reply_markup=IdeaMenu.get(),
        parse_mode="Markdown",
    )


@router.message(SphereToIdeaAssignForm.waiting_for_idea_id)
async def assign_sphere_to_idea_step1(message: types.Message, state: FSMContext):
    raw = (message.text or "").strip()

    try:
        idea_id = int(raw)
    except ValueError:
        return await message.answer("❌ ID ідеї має бути числом. Спробуй ще раз:")

    await state.update_data({KEY_IDEA_ID: idea_id})
    await state.set_state(SphereToIdeaAssignForm.waiting_for_sphere_id)

    spheres_text = await get_all_spheres_text()

    await message.answer(
        "Тепер введи **ID сфери**, яку треба додати до ідеї:\n\n"
        f"{spheres_text}",
        reply_markup=IdeaMenu.get(),
        parse_mode="Markdown",
    )


@router.message(SphereToIdeaAssignForm.waiting_for_sphere_id)
async def assign_sphere_to_idea_step2(message: types.Message, state: FSMContext):
    data = await state.get_data()
    idea_id = data.get(KEY_IDEA_ID)

    raw = (message.text or "").strip()

    try:
        sphere_id = int(raw)
    except ValueError:
        return await message.answer("❌ ID сфери має бути числом. Спробуй ще раз:")

    try:
        dto = SphereToIdeaDTO(sphere_id=sphere_id, idea_id=idea_id)
        is_inserted = await asyncio.to_thread(c.idea_service.assign_sphere_to_idea, dto)

        await state.clear()

        if is_inserted:
            await message.answer(
                "✅ Сферу додано до ідеї!",
                reply_markup=IdeaMenu.get()
            )
        else:
            await message.answer(
                "ℹ️ Ця сфера вже привʼязана до цієї ідеї.",
                reply_markup=IdeaMenu.get()
            )

    except Exception as e:
        logger.exception("Idea assign_sphere_to_idea failed: %s", e)
        await state.clear()
        await message.answer("❌ Сталася помилка під час привʼязки сфери.", reply_markup=IdeaMenu.get())
