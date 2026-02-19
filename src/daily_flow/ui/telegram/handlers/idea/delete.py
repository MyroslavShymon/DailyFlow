import asyncio
import logging

from aiogram import types, F
from aiogram.fsm.context import FSMContext

from daily_flow.ui.telegram.handlers.idea.get import get_all_ideas_text
from daily_flow.ui.telegram.keyboards.idea import IdeaMenu
from daily_flow.ui.telegram.runtime import c, router
from daily_flow.ui.telegram.states import IdeaDeleteForm


logger = logging.getLogger(__name__)

@router.message(F.text == IdeaMenu.BTN_DELETE_IDEA)
async def delete_idea(message: types.Message, state: FSMContext):
    await state.set_state(IdeaDeleteForm.waiting_for_title)

    ideas_text = await get_all_ideas_text()

    await message.answer(
        "Введи точну назву (title) ідеї, яку треба видалити.\n\n"
        f"{ideas_text}",
        reply_markup=IdeaMenu.get(),
        parse_mode="Markdown",
    )


@router.message(IdeaDeleteForm.waiting_for_title)
async def perform_delete_idea(message: types.Message, state: FSMContext):
    title = (message.text or "").strip()

    if not title:
        return await message.answer("❌ Title не може бути порожнім. Введи title ще раз:")

    try:
        deleted = await asyncio.to_thread(c.idea_service.delete_idea_by_title, title)
        await state.clear()

        if deleted > 0:
            await message.answer("✅ Ідею видалено.", reply_markup=IdeaMenu.get())
        else:
            await message.answer("🔍 Ідею з таким title не знайдено (або вже була видалена).", reply_markup=IdeaMenu.get())

    except Exception as e:
        logger.exception("Idea delete_idea_by_title failed: %s", e)
        await state.clear()
        await message.answer("❌ Сталася помилка під час видалення ідеї.", reply_markup=IdeaMenu.get())
