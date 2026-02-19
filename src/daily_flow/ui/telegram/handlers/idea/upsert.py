import logging

from aiogram import types, F, Bot
from aiogram.fsm.context import FSMContext

from daily_flow.ui.telegram.constants.idea import idea_mapping
from daily_flow.ui.telegram.keyboards.idea import IdeaMenu
from daily_flow.ui.telegram.runtime import router
from daily_flow.ui.telegram.states import IdeaForm
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

IDEA_FORM = "idea"

INTENT_VALUES = [
    "problem",
    "solution",
    "hypothesis",
    "question",
    "insight",
    "todo",
]

def _format_intent(value: str | None) -> str:
    if not value:
        return "—"
    pretty = {
        "problem": "🚩 problem",
        "solution": "🛠 solution",
        "hypothesis": "🧪 hypothesis",
        "question": "❓ question",
        "insight": "💡 insight",
        "todo": "📝 todo",
    }
    return pretty.get(value, value)

@router.callback_query(F.data.startswith(f"edit_{IDEA_FORM}:"))
async def edit_any_idea_field(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer()

    field_name = callback.data.split(":")[1]
    await form_set_current_field(state, IDEA_FORM, field_name)

    intent_labels = [
        "🚩 Problem (problem)",
        "🛠 Solution (solution)",
        "🧪 Hypothesis (hypothesis)",
        "❓ Question (question)",
        "💡 Insight (insight)",
        "📝 Todo (todo)",
    ]
    intents_start_index = 0
    intents_button_adjust = [2, 2, 2]
    intents_field_name = "idea_intent"

    if field_name == "intent":
        await callback.message.edit_text(
            f"Оберіть {idea_mapping.get('intent')} для ідеї:",
            reply_markup=build_inline_keyboard(
                field_name=intents_field_name,
                button_names=intent_labels,
                start_index=intents_start_index,
                button_adjusts=intents_button_adjust,
            ),
        )
        return

    await callback.message.edit_text(
        f"Введіть нові дані про {idea_mapping.get(field_name)}:"
    )
    await state.set_state(IdeaForm.waiting_input)

@router.callback_query(F.data.startswith("set_idea_intent_value:"))
async def process_intent_selection(callback: types.CallbackQuery, state: FSMContext, bot: Bot):
    await callback.answer()

    intent_value = INTENT_VALUES[int(callback.data.split(":")[1])]

    await form_set_value(state, IDEA_FORM, "intent", intent_value)
    await form_set_current_field(state, IDEA_FORM, None)

    text = await render_upsert_idea(state)

    await refresh_form_message(
        state=state,
        bot=bot,
        text=text,
        form_name=IDEA_FORM,
        mapping=idea_mapping,
    )

    await callback.answer("✅ Тип ідеї збережено!")

@router.message(IdeaForm.waiting_input)
async def process_idea_input(message: types.Message, state: FSMContext, bot: Bot):
    form: TGForm = await form_get(state, IDEA_FORM)
    field_name = form.get("current_field")

    if not field_name:
        await finish_text_input(state, message, IDEA_FORM)
        await handle_message_error(message, "Упс! Оберіть поле для редагування ще раз.")
        return

    value = (message.text or "").strip()

    if field_name == "title":
        if not value:
            await handle_message_error(message, "❌ Назва (title) не може бути порожньою.")
            return
        await form_set_value(state, IDEA_FORM, "title", value)

    elif field_name == "description":
        if not value:
            await handle_message_error(message, "❌ Опис не може бути порожнім рядком (або не заповнюй його).")
            return
        await form_set_value(state, IDEA_FORM, "description", value)

    else:
        await handle_message_error(message, "❌ Невідоме поле. Спробуй ще раз.")
        return

    text = await render_upsert_idea(state)

    await refresh_form_message(
        state=state,
        bot=bot,
        text=text,
        form_name=IDEA_FORM,
        mapping=idea_mapping,
    )

    await finish_text_input(state, message, IDEA_FORM)

async def render_upsert_idea(state: FSMContext) -> str:
    form: TGForm = await form_get(state, IDEA_FORM)

    idea_data = {
        idea: _format_intent(form["values"].get("intent"))
        if idea == "intent"
        else form["values"].get(idea, "—")
        for idea in idea_mapping.keys()
    }

    text = "💡 **Ідея**\n\n"
    text += "\n".join(
        f"{idea_mapping.get(k).capitalize()}: {v}"
        for k, v in idea_data.items()
    )

    return text

@router.message(F.text == IdeaMenu.BTN_ADD_EDIT_IDEA)
async def show_idea_upsert_form(message: types.Message, state: FSMContext):
    text = await render_upsert_idea(state)

    sent_message = await message.answer(
        text,
        reply_markup=get_form_keyboard(idea_mapping, IDEA_FORM),
        parse_mode="Markdown",
    )

    await form_set_last_msg(
        state=state,
        form_name=IDEA_FORM,
        chat_id=sent_message.chat.id,
        message_id=sent_message.message_id,
    )

    await state.set_state(IdeaForm.waiting_input)