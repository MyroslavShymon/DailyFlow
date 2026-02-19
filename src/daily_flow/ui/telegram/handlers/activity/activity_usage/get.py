import asyncio
import logging

from aiogram import types, F
from aiogram.fsm.context import FSMContext

from daily_flow.services.activity.activity_usage.dto import ActivityUsagePeriodDTO
from daily_flow.ui.telegram.keyboards.activity import ActivityMenu
from daily_flow.ui.telegram.render.activity import render_activity_usage
from daily_flow.ui.telegram.runtime import c, router
from daily_flow.ui.telegram.states import (
    ActivityUsageGetByIdForm,
    ActivityUsageGetByActivityForm,
    ActivityUsageLastForm,
    ActivityUsagePeriodForm,
)
from daily_flow.ui.telegram.utils.datetime_parse import parse_to_datetime
from daily_flow.ui.telegram.utils.truncate_text import truncate_text

logger = logging.getLogger(__name__)

@router.message(F.text == ActivityMenu.BTN_GET_USAGE_BY_ID)
async def ask_usage_id(message: types.Message, state: FSMContext):
    await state.set_state(ActivityUsageGetByIdForm.waiting_for_usage_id)
    await message.answer("Введи **Usage ID**:", reply_markup=ActivityMenu.get(), parse_mode="Markdown")

@router.message(ActivityUsageGetByIdForm.waiting_for_usage_id)
async def perform_get_usage_by_id(message: types.Message, state: FSMContext):
    raw = (message.text or "").strip()
    try:
        usage_id = int(raw)
    except ValueError:
        return await message.answer("❌ Usage ID має бути числом. Спробуй ще раз:")

    try:
        usage = await asyncio.to_thread(c.activity_usage_service.get_activity_usage_by_id, usage_id)
        await state.clear()

        if not usage:
            return await message.answer("🔍 Не знайшов запис виконання.", reply_markup=ActivityMenu.get())

        await message.answer(render_activity_usage(usage), reply_markup=ActivityMenu.get(), parse_mode="Markdown")

    except Exception as e:
        logger.exception("ActivityUsage get_by_id failed: %s", e)
        await state.clear()
        await message.answer("❌ Сталася помилка під час отримання запису.", reply_markup=ActivityMenu.get())

@router.message(F.text == ActivityMenu.BTN_GET_USAGES_BY_ACTIVITY)
async def ask_activity_id_for_usages(message: types.Message, state: FSMContext):
    await state.set_state(ActivityUsageGetByActivityForm.waiting_for_activity_id)
    await message.answer("Введи **Activity ID**, щоб показати історію виконань:", reply_markup=ActivityMenu.get(), parse_mode="Markdown")

@router.message(ActivityUsageGetByActivityForm.waiting_for_activity_id)
async def perform_get_usages_by_activity(message: types.Message, state: FSMContext):
    raw = (message.text or "").strip()
    try:
        activity_id = int(raw)
    except ValueError:
        return await message.answer("❌ Activity ID має бути числом. Спробуй ще раз:")

    try:
        usages = await asyncio.to_thread(c.activity_usage_service.get_activity_usages_by_activity, activity_id)
        await state.clear()

        if not usages:
            return await message.answer("📈 Поки що немає жодного запису виконання.", reply_markup=ActivityMenu.get())

        # компактно
        blocks = "\n\n".join(render_activity_usage(u) for u in usages)
        text = truncate_text(f"📈 **Історія виконань (Activity ID={activity_id})**\n\n{blocks}")
        await message.answer(text, reply_markup=ActivityMenu.get(), parse_mode="Markdown")

    except Exception as e:
        logger.exception("ActivityUsage get_by_activity failed: %s", e)
        await state.clear()
        await message.answer("❌ Сталася помилка під час отримання історії.", reply_markup=ActivityMenu.get())

@router.message(F.text == ActivityMenu.BTN_GET_LAST_USAGES)
async def ask_limit_for_last(message: types.Message, state: FSMContext):
    await state.set_state(ActivityUsageLastForm.waiting_for_limit)
    await message.answer("Введи **limit** (скільки останніх записів показати):", reply_markup=ActivityMenu.get(), parse_mode="Markdown")

@router.message(ActivityUsageLastForm.waiting_for_limit)
async def perform_get_last_usages(message: types.Message, state: FSMContext):
    raw = (message.text or "").strip()
    try:
        limit = int(raw)
    except ValueError:
        return await message.answer("❌ limit має бути числом. Спробуй ще раз:")

    try:
        usages = await asyncio.to_thread(c.activity_usage_service.get_last_activity_usages, limit)
        await state.clear()

        if not usages:
            return await message.answer("🕒 Поки що немає записів.", reply_markup=ActivityMenu.get())

        blocks = "\n\n".join(render_activity_usage(u) for u in usages)
        text = truncate_text(f"🕒 **Останні виконання (limit={limit})**\n\n{blocks}")
        await message.answer(text, reply_markup=ActivityMenu.get(), parse_mode="Markdown")

    except Exception as e:
        logger.exception("ActivityUsage get_last failed: %s", e)
        await state.clear()
        await message.answer("❌ Сталася помилка під час отримання останніх записів.", reply_markup=ActivityMenu.get())

KEY_DATE_FROM = "date_from"

@router.message(F.text == ActivityMenu.BTN_GET_USAGES_BY_PERIOD)
async def ask_period_from(message: types.Message, state: FSMContext):
    await state.set_state(ActivityUsagePeriodForm.waiting_for_date_from)
    await message.answer(
        "DD-MM-YYYY або DD-MM-YYYY HH:MM: це є доступний формат для вводу",
        reply_markup=ActivityMenu.get(),
        parse_mode="Markdown",
    )

@router.message(ActivityUsagePeriodForm.waiting_for_date_from)
async def ask_period_to(message: types.Message, state: FSMContext):
    raw = (message.text or "").strip()
    dt_from = parse_to_datetime(raw)
    if not dt_from:
        return await message.answer("❌ Невірний формат date_from. Спробуй ще раз:")

    await state.update_data({KEY_DATE_FROM: dt_from})
    await state.set_state(ActivityUsagePeriodForm.waiting_for_date_to)

    await message.answer(
        "DD-MM-YYYY або DD-MM-YYYY HH:MM: - це є доступний формат для вводу",
        reply_markup=ActivityMenu.get(),
        parse_mode="Markdown",
    )

@router.message(ActivityUsagePeriodForm.waiting_for_date_to)
async def perform_get_usages_by_period(message: types.Message, state: FSMContext):
    data = await state.get_data()
    dt_from = data.get(KEY_DATE_FROM)

    raw = (message.text or "").strip()
    dt_to = parse_to_datetime(raw)
    if not dt_to:
        return await message.answer("❌ Невірний формат date_to. Спробуй ще раз:")

    try:
        dto = ActivityUsagePeriodDTO(
            date_from = dt_from,
            date_to = dt_to
        )
        usages = await asyncio.to_thread(c.activity_usage_service.get_activity_usages_by_period, dto)

        await state.clear()

        if not usages:
            return await message.answer("📅 За цей період записів немає.", reply_markup=ActivityMenu.get())

        blocks = "\n\n".join(render_activity_usage(u) for u in usages)
        text = truncate_text(f"📅 **Виконання за період**\n\n{blocks}")
        await message.answer(text, reply_markup=ActivityMenu.get(), parse_mode="Markdown")

    except Exception as e:
        logger.exception("ActivityUsage get_by_period failed: %s", e)
        await state.clear()
        await message.answer("❌ Сталася помилка під час отримання записів за період.", reply_markup=ActivityMenu.get())
