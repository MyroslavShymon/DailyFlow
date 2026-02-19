import asyncio
import logging

from aiogram import types, F
from aiogram.fsm.context import FSMContext

from daily_flow.ui.telegram.keyboards.activity import ActivityMenu
from daily_flow.ui.telegram.render.activity import render_category_compact, render_activity_compact
from daily_flow.ui.telegram.runtime import c, router
from daily_flow.ui.telegram.states import ActivityCategoryGetCategoriesForm, ActivityCategoryGetActivitiesForm
from daily_flow.ui.telegram.handlers.activity.activity.get import get_all_activities_text
from daily_flow.ui.telegram.handlers.activity.category.get import get_all_categories_text
from daily_flow.ui.telegram.utils.truncate_text import truncate_text

logger = logging.getLogger(__name__)

@router.message(F.text == ActivityMenu.BTN_GET_CATEGORIES_BY_ACTIVITY)
async def ask_activity_id_for_categories(message: types.Message, state: FSMContext):
    await state.set_state(ActivityCategoryGetCategoriesForm.waiting_for_activity_id)

    activities_text = await get_all_activities_text()

    await message.answer(
        "Введи **Activity ID**, щоб показати категорії цієї активності.\n\n"
        f"{activities_text}",
        reply_markup=ActivityMenu.get(),
        parse_mode="Markdown",
    )

@router.message(ActivityCategoryGetCategoriesForm.waiting_for_activity_id)
async def perform_get_categories_by_activity(message: types.Message, state: FSMContext):
    raw = (message.text or "").strip()

    try:
        activity_id = int(raw)
    except ValueError:
        return await message.answer("❌ Activity ID має бути числом. Спробуй ще раз:")

    try:
        categories = await asyncio.to_thread(c.activity_category_service.get_categories_by_activity, activity_id)
        await state.clear()

        if not categories:
            return await message.answer(f"🏷️ Для Activity ID={activity_id} категорій поки немає.", reply_markup=ActivityMenu.get())

        lines = "\n".join(render_category_compact(cat) for cat in categories)
        text = truncate_text(f"🏷️ **Категорії активності ID={activity_id}**\n\n{lines}")
        await message.answer(text, reply_markup=ActivityMenu.get(), parse_mode="Markdown")

    except Exception as e:
        logger.exception("ActivityCategory get_categories_by_activity failed: %s", e)
        await state.clear()
        await message.answer("❌ Сталася помилка під час отримання категорій.", reply_markup=ActivityMenu.get())

@router.message(F.text == ActivityMenu.BTN_GET_ACTIVITIES_BY_CATEGORY_LINK)
async def ask_category_id_for_activities(message: types.Message, state: FSMContext):
    await state.set_state(ActivityCategoryGetActivitiesForm.waiting_for_category_id)

    categories_text = await get_all_categories_text()

    await message.answer(
        "Введи **Category ID**, щоб показати активності в цій категорії.\n\n"
        f"{categories_text}",
        reply_markup=ActivityMenu.get(),
        parse_mode="Markdown",
    )

@router.message(ActivityCategoryGetActivitiesForm.waiting_for_category_id)
async def perform_get_activities_by_category(message: types.Message, state: FSMContext):
    raw = (message.text or "").strip()

    try:
        category_id = int(raw)
    except ValueError:
        return await message.answer("❌ Category ID має бути числом. Спробуй ще раз:")

    try:
        activities = await asyncio.to_thread(c.activity_category_service.get_activities_by_category, category_id)
        await state.clear()

        if not activities:
            return await message.answer(f"🎯 Для Category ID={category_id} активностей поки немає.", reply_markup=ActivityMenu.get())

        lines = "\n".join(render_activity_compact(a) for a in activities)
        text = truncate_text(f"🎯 **Активності категорії ID={category_id}**\n\n{lines}")
        await message.answer(text, reply_markup=ActivityMenu.get(), parse_mode="Markdown")

    except Exception as e:
        logger.exception("ActivityCategory get_activities_by_category failed: %s", e)
        await state.clear()
        await message.answer("❌ Сталася помилка під час отримання активностей.", reply_markup=ActivityMenu.get())
