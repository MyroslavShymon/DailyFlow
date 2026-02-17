from daily_flow.services.common_mood.dto import UpsertTagImpactDTO, UpsertCommonMoodLogDTO
from daily_flow.services.mood_log.dto import UpsertMoodLogDTO
from daily_flow.ui.telegram.constants.common_mood_log import tag_impact_mapping, common_mood_log_mapping
from daily_flow.ui.telegram.constants.mood_log import mood_log_mapping
from daily_flow.ui.telegram.handlers.common_mood_log.tag.upsert import TAG_IMPACT_FORM
from daily_flow.ui.telegram.handlers.common_mood_log.upsert import COMMON_MOOD_LOG_FORM
from daily_flow.ui.telegram.handlers.mood_log.upsert import MOOD_LOG_FORM
from daily_flow.ui.telegram.render.mood_log import render_mood_log
from daily_flow.ui.telegram.render.сommon_mood_log import render_tag_impact, render_common_mood_log
from daily_flow.ui.telegram.runtime import router, c
from daily_flow.ui.telegram.utils.form_submit import form_submit

from aiogram import types, F, Bot
from aiogram.fsm.context import FSMContext


SUBMIT_FORM_MAPPING = {
    MOOD_LOG_FORM: {
        "values_to_upsert": ["day", "joy", "interest", "calm", "energy", "anxiety", "sadness", "irritation", "fatigue", "fear", "confidence", "sleep"],
        "dto_class": UpsertMoodLogDTO,
        "mapping": mood_log_mapping,
        "upsert_func": c.mood_log_service.upsert_mood_log,
        "render_func": lambda saved, values: render_mood_log(saved),
    },
    TAG_IMPACT_FORM: {
        "values_to_upsert": ["day", "tag", "impact"],
        "dto_class": UpsertTagImpactDTO,
        "mapping": tag_impact_mapping,
        "upsert_func": c.common_mood_log_service.upsert_tag_impact_for_day,
        "render_func": lambda saved, values: render_tag_impact(saved, str(values.get("day") or "—")),
    },
    COMMON_MOOD_LOG_FORM: {
        "values_to_upsert": ["day", "mood", "note"],
        "dto_class": UpsertCommonMoodLogDTO,
        "mapping": common_mood_log_mapping,
        "upsert_func": c.common_mood_log_service.upsert_common_mood_log,
        "render_func": lambda saved, values: render_common_mood_log(saved),
    }
}

@router.callback_query(F.data.startswith("submit_") & F.data.endswith("_form"))
async def submit_form_handler(
        callback: types.CallbackQuery,
        state: FSMContext,
        bot: Bot
):
    data = callback.data
    form_name = data.removeprefix("submit_").removesuffix("_form")

    config = SUBMIT_FORM_MAPPING.get(form_name)
    if not config:
        await callback.answer("Невідома форма", show_alert=True)
        return

    await form_submit(
        callback=callback,
        state=state,
        bot=bot,
        form_name=form_name,
        dto_class=config.get("dto_class"),
        render_func=config.get("render_func"),
        mapping=config.get("mapping"),
        upsert_func=config.get("upsert_func"),
        values_to_upsert=config.get("values_to_upsert"),
    )
