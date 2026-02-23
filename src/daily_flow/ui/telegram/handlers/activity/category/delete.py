import logging

from aiogram import types, F
from aiogram.fsm.context import FSMContext

from daily_flow.app.container import Container
from daily_flow.ui.telegram.keyboards.activity import ActivityMenu
from daily_flow.ui.telegram.runtime import router
from daily_flow.ui.telegram.states import CategoryDeleteForm
from daily_flow.ui.telegram.handlers.activity.category.get import get_all_categories_text


logger = logging.getLogger(__name__)

@router.message(F.text == ActivityMenu.BTN_DELETE_CATEGORY)
async def delete_category(message: types.Message, state: FSMContext, db_container: Container):
    await state.set_state(CategoryDeleteForm.waiting_for_ref)

    categories_text = await get_all_categories_text(db_container)

    await message.answer(
        "Введи **ID** або **назву (name)** категорії, яку треба видалити.\n\n"
        f"{categories_text}",
        reply_markup=ActivityMenu.get(),
        parse_mode="Markdown",
    )


@router.message(CategoryDeleteForm.waiting_for_ref)
async def perform_delete_category(message: types.Message, state: FSMContext, db_container: Container):
    ref = (message.text or "").strip()
    if not ref:
        return await message.answer("❌ Введи ID або name ще раз:")

    try:
        if ref.isdigit():
            deleted = await db_container.category_service.delete_category_by_id(int(ref))
        else:
            deleted = await db_container.category_service.delete_category_by_name(ref)

        await state.clear()

        if deleted > 0:
            await message.answer("✅ Категорію видалено.", reply_markup=ActivityMenu.get())
        else:
            await message.answer("🔍 Нічого не видалено (не знайшов запис).", reply_markup=ActivityMenu.get())

    except Exception as e:
        logger.exception("Category delete failed: %s", e)
        await state.clear()
        await message.answer("❌ Сталася помилка під час видалення категорії.", reply_markup=ActivityMenu.get())
