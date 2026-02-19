import asyncio
import logging

from aiogram import types, F
from aiogram.fsm.context import FSMContext

from daily_flow.ui.telegram.keyboards.activity import ActivityMenu
from daily_flow.ui.telegram.runtime import c, router
from daily_flow.ui.telegram.states import ActivityDeleteForm
from daily_flow.ui.telegram.handlers.activity.activity.get import get_all_activities_text


logger = logging.getLogger(__name__)

@router.message(F.text == ActivityMenu.BTN_DELETE_ACTIVITY)
async def delete_activity(message: types.Message, state: FSMContext):
    await state.set_state(ActivityDeleteForm.waiting_for_ref)

    activities_text = await get_all_activities_text()

    await message.answer(
        "Введи **ID** або **назву (title)** активності, яку треба видалити.\n\n"
        f"{activities_text}",
        reply_markup=ActivityMenu.get(),
        parse_mode="Markdown",
    )


@router.message(ActivityDeleteForm.waiting_for_ref)
async def perform_delete_activity(message: types.Message, state: FSMContext):
    ref = (message.text or "").strip()
    if not ref:
        return await message.answer("❌ Введи ID або title ще раз:")

    try:
        if ref.isdigit():
            deleted = await asyncio.to_thread(c.activity_service.delete_activity_by_id, int(ref))
        else:
            deleted = await asyncio.to_thread(c.activity_service.delete_activity_by_title, ref)

        await state.clear()

        if deleted > 0:
            await message.answer("✅ Активність видалено.", reply_markup=ActivityMenu.get())
        else:
            await message.answer("🔍 Нічого не видалено (не знайшов запис).", reply_markup=ActivityMenu.get())

    except Exception as e:
        logger.exception("Activity delete failed: %s", e)
        await state.clear()
        await message.answer("❌ Сталася помилка під час видалення активності.", reply_markup=ActivityMenu.get())
