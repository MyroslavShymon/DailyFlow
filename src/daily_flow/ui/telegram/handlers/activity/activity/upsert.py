import logging

from aiogram import types, F, Bot
from aiogram.fsm.context import FSMContext

from daily_flow.ui.telegram.constants.activity import activity_mapping
from daily_flow.ui.telegram.keyboards.activity import ActivityMenu
from daily_flow.ui.telegram.runtime import router
from daily_flow.ui.telegram.states import ActivityForm
from daily_flow.ui.telegram.utils.errors import handle_message_error
from daily_flow.ui.telegram.utils.form_render import get_form_keyboard
from daily_flow.ui.telegram.utils.forms_state import (
    TGForm,
    form_get,
    form_set_last_msg,
    form_set_value,
    form_set_current_field,
    refresh_form_message,
    finish_text_input,
)
from daily_flow.ui.telegram.utils.keyboard import build_inline_keyboard

logger = logging.getLogger(__name__)

ACTIVITY_FORM = "activity"

SOCIAL_TYPE_VALUES = ["solo", "couple", "friends", "family", "any"]
SOCIAL_TYPE_LABELS = ["👤 Сам", "💑 Пара", "👯 Друзі", "👪 Сімʼя", "🌈 Будь-як"]

TIME_CONTEXT_VALUES = ["weekday", "weekend", "vacation", "any"]
TIME_CONTEXT_LABELS = ["📅 Будні", "🏖️ Вихідні", "✈️ Відпустка", "🌈 Будь-коли"]

TIME_OF_DAY_VALUES = ["morning", "day", "evening", "night", "flexible"]
TIME_OF_DAY_LABELS = ["🌅 Ранок", "🌤 День", "🌆 Вечір", "🌙 Ніч", "🌀 Гнучко"]

COST_LEVEL_VALUES = ["free", "low", "medium", "high"]
COST_LEVEL_LABELS = ["🆓 Безкоштовно", "💸 Дешево", "💰 Середньо", "💎 Дорого"]

LOCATION_TYPE_VALUES = ["home", "city", "nature", "any"]
LOCATION_TYPE_LABELS = ["🏠 Дім", "🏙 Місто", "🌲 Природа", "🌈 Будь-де"]

PREP_VALUES = [False, True]
PREP_LABELS = ["❌ ні", "✅ так"]

@router.callback_query(F.data.startswith(f"edit_{ACTIVITY_FORM}:"))
async def edit_any_activity_field(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer()

    field_name = callback.data.split(":")[1]
    await form_set_current_field(state, ACTIVITY_FORM, field_name)

    if field_name == "social_type":
        await callback.message.edit_text(
            "👥 **Соціальний формат**\n\n"
            "Як плануєш робити цю активність?\n"
            "Обери варіант нижче:",
            reply_markup=build_inline_keyboard(
                field_name="activity_social_type",
                button_names=SOCIAL_TYPE_LABELS,
                start_index=0,
                button_adjusts=[3, 2],
            ),
        )
        return

    if field_name == "time_context":
        await callback.message.edit_text(
            "📅 **Контекст часу**\n\n"
            "Коли ця активність найбільш доречна?\n"
            "Обери: будній / вихідний / відпустка / будь-коли.",
            reply_markup=build_inline_keyboard(
                field_name="activity_time_context",
                button_names=TIME_CONTEXT_LABELS,
                start_index=0,
                button_adjusts=[2, 2],
            ),
        )
        return

    if field_name == "time_of_day":
        await callback.message.edit_text(
            "🕒 **Час доби**\n\n"
            "Коли зручніше робити цю активність?\n"
            "Обери оптимальний варіант:",
            reply_markup=build_inline_keyboard(
                field_name="activity_time_of_day",
                button_names=TIME_OF_DAY_LABELS,
                start_index=0,
                button_adjusts=[3, 2],
            ),
        )
        return

    if field_name == "cost_level":
        await callback.message.edit_text(
            "💸 **Рівень витрат**\n\n"
            "Оціни приблизно, наскільки це дорого.\n"
            "Якщо активність безкоштовна — обирай **free**.",
            reply_markup=build_inline_keyboard(
                field_name="activity_cost_level",
                button_names=COST_LEVEL_LABELS,
                start_index=0,
                button_adjusts=[2, 2],
            ),
        )
        return

    if field_name == "location_type":
        await callback.message.edit_text(
            "📍 **Тип локації**\n\n"
            "Де ця активність найкраще підходить?\n"
            "Обери варіант нижче:",
            reply_markup=build_inline_keyboard(
                field_name="activity_location_type",
                button_names=LOCATION_TYPE_LABELS,
                start_index=0,
                button_adjusts=[2, 2],
            ),
        )
        return

    if field_name == "requires_preparation":
        await callback.message.edit_text(
            "🧰 **Підготовка**\n\n"
            "Чи потрібно щось підготувати заздалегідь?\n"
            "Наприклад: зібрати речі, купити щось, забронювати.",
            reply_markup=build_inline_keyboard(
                field_name="activity_requires_preparation",
                button_names=PREP_LABELS,
                start_index=0,
                button_adjusts=[2],
            ),
        )
        return

    field_label = activity_mapping.get(field_name, field_name)

    await callback.message.edit_text(
        "✏️ **Редагування поля**\n\n"
        f"Введіть нове значення для:\n"
        f"**{field_label}**\n\n"
        "Підказка:\n"
        "• якщо поле не обовʼязкове — можна написати `-` щоб очистити\n"
        "• числа вводь без зайвих символів (наприклад `90`)\n",
    )
    await state.set_state(ActivityForm.waiting_input)


@router.callback_query(F.data.startswith("set_activity_social_type_value:"))
async def process_social_type_selection(callback: types.CallbackQuery, state: FSMContext, bot: Bot):
    await callback.answer()
    social_type_value = int(callback.data.split(":")[1])

    if social_type_value < 0 or social_type_value >= len(SOCIAL_TYPE_VALUES):
        return await callback.answer("❌ Невірний вибір", show_alert=True)

    await form_set_value(state, ACTIVITY_FORM, "social_type", SOCIAL_TYPE_VALUES[social_type_value])
    await form_set_current_field(state, ACTIVITY_FORM, None)

    text = await render_upsert_activity(state)
    await refresh_form_message(state=state, bot=bot, text=text, form_name=ACTIVITY_FORM, mapping=activity_mapping)
    await callback.answer("✅ Збережено!")


@router.callback_query(F.data.startswith("set_activity_time_context_value:"))
async def process_time_context_selection(callback: types.CallbackQuery, state: FSMContext, bot: Bot):
    await callback.answer()
    time_context_value = int(callback.data.split(":")[1])

    if time_context_value < 0 or time_context_value >= len(TIME_CONTEXT_VALUES):
        return await callback.answer("❌ Невірний вибір", show_alert=True)

    await form_set_value(state, ACTIVITY_FORM, "time_context", TIME_CONTEXT_VALUES[time_context_value])
    await form_set_current_field(state, ACTIVITY_FORM, None)

    text = await render_upsert_activity(state)
    await refresh_form_message(state=state, bot=bot, text=text, form_name=ACTIVITY_FORM, mapping=activity_mapping)
    await callback.answer("✅ Збережено!")


@router.callback_query(F.data.startswith("set_activity_time_of_day_value:"))
async def process_time_of_day_selection(callback: types.CallbackQuery, state: FSMContext, bot: Bot):
    await callback.answer()
    time_of_day_value = int(callback.data.split(":")[1])

    if time_of_day_value < 0 or time_of_day_value >= len(TIME_OF_DAY_VALUES):
        return await callback.answer("❌ Невірний вибір", show_alert=True)

    await form_set_value(state, ACTIVITY_FORM, "time_of_day", TIME_OF_DAY_VALUES[time_of_day_value])
    await form_set_current_field(state, ACTIVITY_FORM, None)

    text = await render_upsert_activity(state)
    await refresh_form_message(state=state, bot=bot, text=text, form_name=ACTIVITY_FORM, mapping=activity_mapping)
    await callback.answer("✅ Збережено!")


@router.callback_query(F.data.startswith("set_activity_cost_level_value:"))
async def process_cost_level_selection(callback: types.CallbackQuery, state: FSMContext, bot: Bot):
    await callback.answer()
    cost_level_value = int(callback.data.split(":")[1])

    if cost_level_value < 0 or cost_level_value >= len(COST_LEVEL_VALUES):
        return await callback.answer("❌ Невірний вибір", show_alert=True)

    await form_set_value(state, ACTIVITY_FORM, "cost_level", COST_LEVEL_VALUES[cost_level_value])
    await form_set_current_field(state, ACTIVITY_FORM, None)

    text = await render_upsert_activity(state)
    await refresh_form_message(state=state, bot=bot, text=text, form_name=ACTIVITY_FORM, mapping=activity_mapping)
    await callback.answer("✅ Збережено!")


@router.callback_query(F.data.startswith("set_activity_location_type_value:"))
async def process_location_type_selection(callback: types.CallbackQuery, state: FSMContext, bot: Bot):
    await callback.answer()
    location_type_value = int(callback.data.split(":")[1])

    if location_type_value < 0 or location_type_value >= len(LOCATION_TYPE_VALUES):
        return await callback.answer("❌ Невірний вибір", show_alert=True)

    await form_set_value(state, ACTIVITY_FORM, "location_type", LOCATION_TYPE_VALUES[location_type_value])
    await form_set_current_field(state, ACTIVITY_FORM, None)

    text = await render_upsert_activity(state)
    await refresh_form_message(state=state, bot=bot, text=text, form_name=ACTIVITY_FORM, mapping=activity_mapping)
    await callback.answer("✅ Збережено!")


@router.callback_query(F.data.startswith("set_activity_requires_preparation_value:"))
async def process_requires_preparation_selection(callback: types.CallbackQuery, state: FSMContext, bot: Bot):
    await callback.answer()
    requires_preparation_value = int(callback.data.split(":")[1])

    if requires_preparation_value < 0 or requires_preparation_value >= len(PREP_VALUES):
        return await callback.answer("❌ Невірний вибір", show_alert=True)

    await form_set_value(state, ACTIVITY_FORM, "requires_preparation", PREP_VALUES[requires_preparation_value])
    await form_set_current_field(state, ACTIVITY_FORM, None)

    text = await render_upsert_activity(state)
    await refresh_form_message(state=state, bot=bot, text=text, form_name=ACTIVITY_FORM, mapping=activity_mapping)
    await callback.answer("✅ Збережено!")

@router.message(ActivityForm.waiting_input)
async def process_activity_input(
        message: types.Message,
        state: FSMContext,
        bot: Bot
):
    form: TGForm = await form_get(state, ACTIVITY_FORM)
    field_name = form.get("current_field")

    if not field_name:
        await finish_text_input(state, message, ACTIVITY_FORM)
        await handle_message_error(message, "Упс! Оберіть поле для редагування ще раз.")
        return

    value = (message.text or "").strip()

    if not value:
        await handle_message_error(message, "❌ Значення не може бути порожнім.")
        return

    await form_set_value(state, ACTIVITY_FORM, field_name, value)

    text = await render_upsert_activity(state)

    await refresh_form_message(
        state=state,
        bot=bot,
        text=text,
        form_name=ACTIVITY_FORM,
        mapping=activity_mapping
    )

    await finish_text_input(state, message, ACTIVITY_FORM)

async def render_upsert_activity(state: FSMContext) -> str:
    form: TGForm = await form_get(state, ACTIVITY_FORM)

    values = form["values"]

    def val(k: str) -> str:
        v = values.get(k, None)
        if v is None:
            return "—"
        if k == "requires_preparation":
            if isinstance(v, bool):
                return "✅ так" if v else "❌ ні"
            return "—"
        return str(v)

    text = "🎯 **Активність**\n\n"
    text += "\n".join(f"{activity_mapping.get(k).capitalize()}: {val(k)}" for k in activity_mapping.keys())
    return text

@router.message(F.text == ActivityMenu.BTN_ADD_EDIT_ACTIVITY)
async def show_activity_upsert_form(message: types.Message, state: FSMContext):
    text = await render_upsert_activity(state)

    sent_message = await message.answer(
        text,
        reply_markup=get_form_keyboard(activity_mapping, ACTIVITY_FORM),
        parse_mode="Markdown",
    )

    await form_set_last_msg(
        state=state,
        form_name=ACTIVITY_FORM,
        chat_id=sent_message.chat.id,
        message_id=sent_message.message_id
    )

    await state.set_state(ActivityForm.waiting_input)
