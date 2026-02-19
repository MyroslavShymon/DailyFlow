import asyncio
import logging

from aiogram import types, F
from aiogram.fsm.context import FSMContext

from daily_flow.ui.telegram.keyboards.activity import ActivityMenu
from daily_flow.ui.telegram.runtime import c, router
from daily_flow.ui.telegram.states import ActivityUsageDeleteForm, ActivityUsageDeleteByActivityForm

logger = logging.getLogger(__name__)

@router.message(F.text == ActivityMenu.BTN_DELETE_USAGE)
async def delete_usage(message: types.Message, state: FSMContext):
    await state.set_state(ActivityUsageDeleteForm.waiting_for_usage_id)
    await message.answer("Введи **Usage ID**, який треба видалити:", reply_markup=ActivityMenu.get(), parse_mode="Markdown")

@router.message(ActivityUsageDeleteForm.waiting_for_usage_id)
async def perform_delete_usage(message: types.Message, state: FSMContext):
    raw = (message.text or "").strip()
    try:
        usage_id = int(raw)
    except ValueError:
        return await message.answer("❌ Usage ID має бути числом. Спробуй ще раз:")

    try:
        deleted = await asyncio.to_thread(c.activity_usage_service.delete_activity_usage_by_id, usage_id)
        await state.clear()

        if deleted > 0:
            await message.answer("✅ Запис виконання видалено.", reply_markup=ActivityMenu.get())
        else:
            await message.answer("🔍 Нічого не видалено (не знайшов usage).", reply_markup=ActivityMenu.get())

    except Exception as e:
        logger.exception("ActivityUsage delete_by_id failed: %s", e)
        await state.clear()
        await message.answer("❌ Сталася помилка під час видалення.", reply_markup=ActivityMenu.get())

@router.message(F.text == ActivityMenu.BTN_DELETE_USAGES_BY_ACTIVITY)
async def delete_usages_by_activity(message: types.Message, state: FSMContext):
    await state.set_state(ActivityUsageDeleteByActivityForm.waiting_for_activity_id)
    await message.answer("Введи **Activity ID**, для якого треба очистити історію:", reply_markup=ActivityMenu.get(), parse_mode="Markdown")

@router.message(ActivityUsageDeleteByActivityForm.waiting_for_activity_id)
async def perform_delete_usages_by_activity(message: types.Message, state: FSMContext):
    raw = (message.text or "").strip()
    try:
        activity_id = int(raw)
    except ValueError:
        return await message.answer("❌ Activity ID має бути числом. Спробуй ще раз:")

    try:
        deleted = await asyncio.to_thread(c.activity_usage_service.delete_activity_usages_by_activity, activity_id)
        await state.clear()

        if deleted > 0:
            await message.answer(f"✅ Видалено записів: {deleted}", reply_markup=ActivityMenu.get())
        else:
            await message.answer("🔍 Нічого не видалено (записів не було).", reply_markup=ActivityMenu.get())

    except Exception as e:
        logger.exception("ActivityUsage delete_by_activity failed: %s", e)
        await state.clear()
        await message.answer("❌ Сталася помилка під час очищення історії.", reply_markup=ActivityMenu.get())