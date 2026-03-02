import logging

from aiogram import F, types
from aiogram.fsm.context import FSMContext

from daily_flow.app.container import Container
from daily_flow.ui.telegram.handlers.activity.activity.get import get_all_activities_text
from daily_flow.ui.telegram.keyboards.activity import ActivityMenu
from daily_flow.ui.telegram.runtime import router
from daily_flow.ui.telegram.states import ActivityDeleteForm

logger = logging.getLogger(__name__)


@router.message(F.text == ActivityMenu.BTN_DELETE_ACTIVITY)
async def delete_activity(message: types.Message, state: FSMContext, db_container: Container):
    await state.set_state(ActivityDeleteForm.waiting_for_ref)

    activities_text = await get_all_activities_text(db_container)

    await message.answer(
        f"Введи **ID** або **назву (title)** активності, яку треба видалити.\n\n{activities_text}",
        reply_markup=ActivityMenu.get(),
        parse_mode="Markdown",
    )


@router.message(ActivityDeleteForm.waiting_for_ref)
async def perform_delete_activity(
    message: types.Message, state: FSMContext, db_container: Container
):
    ref = (message.text or "").strip()
    if not ref:
        return await message.answer("❌ Введи ID або title ще раз:")

    try:
        if ref.isdigit():
            deleted = await db_container.activity_service.delete_activity_by_id(int(ref))
        else:
            deleted = await db_container.activity_service.delete_activity_by_title(ref)

        await state.clear()

        if deleted > 0:
            await message.answer("✅ Активність видалено.", reply_markup=ActivityMenu.get())
        else:
            await message.answer(
                "🔍 Нічого не видалено (не знайшов запис).", reply_markup=ActivityMenu.get()
            )

    except Exception as e:
        logger.exception("Activity delete failed: %s", e)
        await state.clear()
        await message.answer(
            "❌ Сталася помилка під час видалення активності.", reply_markup=ActivityMenu.get()
        )
