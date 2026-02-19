import asyncio
import logging

from aiogram import types, F
from aiogram.fsm.context import FSMContext

from daily_flow.ui.telegram.keyboards.activity import ActivityMenu
from daily_flow.ui.telegram.render.activity import render_activity_compact, render_activity
from daily_flow.ui.telegram.runtime import c, router
from daily_flow.ui.telegram.states import ActivityGetForm, ActivityByCategoryGetForm
from daily_flow.ui.telegram.handlers.activity.category.get import get_all_categories_text
from daily_flow.ui.telegram.utils.truncate_text import truncate_text

logger = logging.getLogger(__name__)

async def get_all_activities_text() -> str:
    activities = await asyncio.to_thread(c.activity_service.get_all_activities)

    if not activities:
        return "🎯 Поки що немає жодної активності."

    lines = "\n".join(render_activity_compact(a) for a in activities)
    text = "🎯 **Список активностей**\n\n" + lines
    return truncate_text(text)


@router.message(F.text == ActivityMenu.BTN_GET_ALL_ACTIVITIES)
async def get_all_activities(message: types.Message):
    try:
        text = await get_all_activities_text()
        await message.answer(text, reply_markup=ActivityMenu.get(), parse_mode="Markdown")
    except Exception as e:
        logger.exception("Activity get_all_activities failed: %s", e)
        await message.answer("❌ Сталася помилка під час отримання списку активностей.", reply_markup=ActivityMenu.get())


@router.message(F.text == ActivityMenu.BTN_GET_ACTIVITY)
async def ask_activity_ref(message: types.Message, state: FSMContext):
    await state.set_state(ActivityGetForm.waiting_for_ref)

    activities_text = await get_all_activities_text()

    await message.answer(
        "Введи **ID** або **назву (title)** активності.\n\n"
        f"{activities_text}",
        reply_markup=ActivityMenu.get(),
        parse_mode="Markdown",
    )


@router.message(ActivityGetForm.waiting_for_ref)
async def perform_get_activity(message: types.Message, state: FSMContext):
    ref = (message.text or "").strip()
    if not ref:
        return await message.answer("❌ Введи ID або title ще раз:")

    try:
        if ref.isdigit():
            activity_id = int(ref)
            activity = await asyncio.to_thread(c.activity_service.get_activity_by_id, activity_id)
        else:
            activity = await asyncio.to_thread(c.activity_service.get_activity_by_title, ref)

        await state.clear()

        if not activity:
            return await message.answer("🔍 Не знайшов активність за цим значенням.", reply_markup=ActivityMenu.get())

        await message.answer(render_activity(activity), reply_markup=ActivityMenu.get(), parse_mode="Markdown")

    except Exception as e:
        logger.exception("Activity get failed: %s", e)
        await state.clear()
        await message.answer("❌ Сталася помилка під час пошуку активності.", reply_markup=ActivityMenu.get())


@router.message(F.text == ActivityMenu.BTN_GET_ACTIVITIES_BY_CATEGORY)
async def ask_category_for_activities(message: types.Message, state: FSMContext):
    await state.set_state(ActivityByCategoryGetForm.waiting_for_category_id)

    categories_text = await get_all_categories_text()

    await message.answer(
        "Введи **ID категорії**, щоб показати активності в ній.\n\n"
        f"{categories_text}",
        reply_markup=ActivityMenu.get(),
        parse_mode="Markdown",
    )


@router.message(ActivityByCategoryGetForm.waiting_for_category_id)
async def perform_get_activities_by_category(message: types.Message, state: FSMContext):
    raw = (message.text or "").strip()

    try:
        category_id = int(raw)
    except ValueError:
        return await message.answer("❌ ID категорії має бути числом. Спробуй ще раз:")

    try:
        activities = await asyncio.to_thread(c.activity_service.get_activities_by_category, category_id)

        await state.clear()

        if not activities:
            return await message.answer(f"📌 За категорією ID={category_id} активностей поки немає.", reply_markup=ActivityMenu.get())

        lines = "\n".join(render_activity_compact(a) for a in activities)
        text = truncate_text(f"📌 **Активності за категорією ID={category_id}**\n\n{lines}")
        await message.answer(text, reply_markup=ActivityMenu.get(), parse_mode="Markdown")

    except Exception as e:
        logger.exception("Activity get_activities_by_category failed: %s", e)
        await state.clear()
        await message.answer("❌ Сталася помилка під час отримання активностей за категорією.", reply_markup=ActivityMenu.get())
