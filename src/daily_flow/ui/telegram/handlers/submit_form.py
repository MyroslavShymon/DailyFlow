from daily_flow.services.activity.activity.dto import UpsertActivityDTO
from daily_flow.services.activity.activity_category.dto import CategoryToActivityDTO
from daily_flow.services.activity.activity_usage.dto import UpsertActivityUsageDTO
from daily_flow.services.activity.category.dto import UpsertCategoryDTO
from daily_flow.services.common_mood.dto import UpsertTagImpactDTO, UpsertCommonMoodLogDTO
from daily_flow.services.idea.dto import UpsertIdeaDTO, UpsertSphereDTO
from daily_flow.services.mood_log.dto import UpsertMoodLogDTO
from daily_flow.ui.telegram.constants.activity import activity_mapping, category_mapping, activity_category_mapping, \
    activity_usage_mapping
from daily_flow.ui.telegram.constants.common_mood_log import tag_impact_mapping, common_mood_log_mapping
from daily_flow.ui.telegram.constants.idea import idea_mapping, sphere_mapping
from daily_flow.ui.telegram.constants.mood_log import mood_log_mapping
from daily_flow.ui.telegram.handlers.activity.activity.upsert import ACTIVITY_FORM
from daily_flow.ui.telegram.handlers.activity.activity_category.upsert import ACTIVITY_CATEGORY_FORM
from daily_flow.ui.telegram.handlers.activity.activity_usage.upsert import ACTIVITY_USAGE_FORM
from daily_flow.ui.telegram.handlers.activity.category.upsert import CATEGORY_FORM
from daily_flow.ui.telegram.handlers.common_mood_log.tag.upsert import TAG_IMPACT_FORM
from daily_flow.ui.telegram.handlers.common_mood_log.upsert import COMMON_MOOD_LOG_FORM
from daily_flow.ui.telegram.handlers.idea.sphere.upsert import SPHERE_FORM
from daily_flow.ui.telegram.handlers.idea.upsert import IDEA_FORM
from daily_flow.ui.telegram.handlers.mood_log.upsert import MOOD_LOG_FORM
from daily_flow.ui.telegram.render.activity import render_activity, render_assign_category_result, \
    render_activity_usage, render_category
from daily_flow.ui.telegram.render.idea import render_idea, render_sphere
from daily_flow.ui.telegram.render.mood_log import render_mood_log
from daily_flow.ui.telegram.render.сommon_mood_log import render_tag_impact, render_common_mood_log
from daily_flow.ui.telegram.runtime import router, c
from daily_flow.ui.telegram.utils.form_submit import form_submit

from aiogram import types, F, Bot
from aiogram.fsm.context import FSMContext


SUBMIT_FORM_MAPPING = {
    IDEA_FORM: {
        "values_to_upsert": ["title", "description", "intent"],
        "dto_class": UpsertIdeaDTO,
        "mapping": idea_mapping,
        "upsert_func": c.idea_service.upsert_idea,
        "render_func": lambda saved, values: render_idea(saved),
    },
    SPHERE_FORM: {
        "values_to_upsert": ["name", "description"],
        "dto_class": UpsertSphereDTO,
        "mapping": sphere_mapping,
        "upsert_func": c.idea_service.upsert_sphere,
        "render_func": lambda saved, values: render_sphere(saved),
    },
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
    },
    ACTIVITY_FORM: {
        "values_to_upsert": list(activity_mapping.keys()),
        "dto_class": UpsertActivityDTO,
        "mapping": activity_mapping,
        "upsert_func": c.activity_service.upsert_activity,
        "render_func": lambda saved, values: render_activity(saved),
    },
    CATEGORY_FORM: {
        "values_to_upsert": list(category_mapping.keys()),
        "dto_class": UpsertCategoryDTO,
        "mapping": category_mapping,
        "upsert_func": c.category_service.upsert_category,
        "render_func": lambda saved, values: render_category(saved),
    },
    ACTIVITY_CATEGORY_FORM: {
        "values_to_upsert": list(activity_category_mapping.keys()),
        "dto_class": CategoryToActivityDTO,
        "mapping": activity_category_mapping,
        "upsert_func": c.activity_category_service.assign_category_to_activity,
        "render_func": lambda saved, values: render_assign_category_result(saved, values),
    },
    ACTIVITY_USAGE_FORM: {
        "values_to_upsert": list(activity_usage_mapping.keys()),
        "dto_class": UpsertActivityUsageDTO,
        "mapping": activity_usage_mapping,
        "upsert_func": c.activity_usage_service.upsert_activity_usage,
        "render_func": lambda saved, values: render_activity_usage(saved),
    },
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
