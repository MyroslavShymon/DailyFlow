import logging

from aiogram import types, F
from aiogram.fsm.context import FSMContext

from daily_flow.app.container import Container
from daily_flow.services.activity.activity_category.dto import CategoryToActivityDTO
from daily_flow.ui.telegram.keyboards.activity import ActivityMenu
from daily_flow.ui.telegram.runtime import router
from daily_flow.ui.telegram.states import ActivityCategoryAssignDeleteForm


logger = logging.getLogger(__name__)

KEY_ACTIVITY_ID = "activity_id_to_unassign"

@router.message(F.text == ActivityMenu.BTN_DELETE_CATEGORY_FROM_ACTIVITY)
async def delete_category_from_activity(message: types.Message, state: FSMContext):
    await state.set_state(ActivityCategoryAssignDeleteForm.waiting_for_activity_id)
    await message.answer("Введи **Activity ID**, з якого треба прибрати категорію:", reply_markup=ActivityMenu.get(), parse_mode="Markdown")

@router.message(ActivityCategoryAssignDeleteForm.waiting_for_activity_id)
async def delete_category_from_activity_step1(message: types.Message, state: FSMContext):
    raw = (message.text or "").strip()
    try:
        activity_id = int(raw)
    except ValueError:
        return await message.answer("❌ Activity ID має бути числом. Спробуй ще раз:")

    await state.update_data({KEY_ACTIVITY_ID: activity_id})
    await state.set_state(ActivityCategoryAssignDeleteForm.waiting_for_category_id)
    await message.answer("Тепер введи **Category ID**, яку треба прибрати:", reply_markup=ActivityMenu.get(), parse_mode="Markdown")

@router.message(ActivityCategoryAssignDeleteForm.waiting_for_category_id)
async def delete_category_from_activity_step2(message: types.Message, state: FSMContext, db_container: Container):
    data = await state.get_data()
    activity_id = data.get(KEY_ACTIVITY_ID)

    raw = (message.text or "").strip()
    try:
        category_id = int(raw)
    except ValueError:
        return await message.answer("❌ Category ID має бути числом. Спробуй ще раз:")

    try:
        dto = CategoryToActivityDTO(
            category_id = category_id,
            activity_id = activity_id
        )

        deleted = await db_container.activity_category_service.delete_category_from_activity(dto)  # process_dto не використовуємо у delete
        await state.clear()

        if deleted > 0:
            await message.answer("✅ Звʼязок видалено.", reply_markup=ActivityMenu.get())
        else:
            await message.answer("🔍 Нічого не видалено (звʼязок не знайдено).", reply_markup=ActivityMenu.get())

    except Exception as e:
        logger.exception("ActivityCategory delete failed: %s", e)
        await state.clear()
        await message.answer("❌ Сталася помилка під час видалення звʼязку.", reply_markup=ActivityMenu.get())
