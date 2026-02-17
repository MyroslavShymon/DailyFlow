import logging

from aiogram import types, F, Bot
from aiogram.fsm.context import FSMContext

from daily_flow.ui.telegram.constants.common_mood_log import tag_impact_mapping
from daily_flow.ui.telegram.handlers.common_mood_log.tag.get import get_all_tags, get_all_tags_text
from daily_flow.ui.telegram.keyboards.common_mood import CommonMoodMenu
from daily_flow.ui.telegram.runtime import router
from daily_flow.ui.telegram.states import TagImpactForm
from daily_flow.ui.telegram.utils.date_parse import parse_to_date
from daily_flow.ui.telegram.utils.errors import handle_message_error
from daily_flow.ui.telegram.utils.form_render import get_form_keyboard
from daily_flow.ui.telegram.utils.forms_state import form_set_last_msg, TGForm, form_get, form_set_value, \
    form_set_current_field, refresh_form_message, finish_text_input
from daily_flow.ui.telegram.utils.keyboard import build_inline_keyboard


logger = logging.getLogger(__name__)

TAG_IMPACT_FORM = "tag_impact"

@router.callback_query(F.data.startswith(f"edit_{TAG_IMPACT_FORM}:"))
async def edit_any_tag_impact_field(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer()

    field_name = callback.data.split(":")[1]
    await form_set_current_field(state, TAG_IMPACT_FORM, field_name)

    impacts = ["🔻 Негативно впливає",  "🟡 Нейтрально (важко визначити)", "☘️ Позитивно впливає"]
    impacts_start_index = -1
    impacts_button_adjust = [3]
    impacts_field_name = "impact"

    if field_name == "impact":
        await callback.message.edit_text(
            "Оберіть рівень впливу на настрій:",
            reply_markup=build_inline_keyboard(
                field_name=impacts_field_name,
                button_names=impacts,
                start_index=impacts_start_index,
                button_adjusts=impacts_button_adjust
            )
        )
    elif field_name == "tag":
        tags_text = await get_all_tags_text(state)
        await callback.message.edit_text(f"Введіть ваші нові дані про {tag_impact_mapping.get('tag')}: \n {tags_text}")
        await state.set_state(TagImpactForm.waiting_input)
    else:
        await callback.message.edit_text(f"Введіть ваші нові дані про {tag_impact_mapping.get(field_name)}:")
        await state.set_state(TagImpactForm.waiting_input)

@router.callback_query(F.data.startswith("set_impact_value:"))
async def process_impact_value(callback: types.CallbackQuery, state: FSMContext, bot: Bot):
    await callback.answer()
    impact_value = int(callback.data.split(":")[1])

    await form_set_value(state, TAG_IMPACT_FORM, "impact", impact_value)
    await form_set_current_field(state, TAG_IMPACT_FORM, None)

    text = await render_upsert_impact(state)

    await refresh_form_message(
        text=text,
        state=state,
        bot=bot,
        form_name=TAG_IMPACT_FORM,
        mapping=tag_impact_mapping
    )

    await callback.answer(f"Вплив чинника збережено!")

@router.message(TagImpactForm.waiting_input)
async def process_tag_impact_input(
        message: types.Message,
        state: FSMContext,
        bot: Bot
):
    form: TGForm = await form_get(state, TAG_IMPACT_FORM)
    field_name = form["current_field"]

    if not field_name:
        await finish_text_input(state, message, TAG_IMPACT_FORM)
        await handle_message_error(message, "Упс! Оберіть поле для редагування ще раз.")
        return

    if field_name == "day":
        valid_date = parse_to_date(message.text)
        if not valid_date:
            await handle_message_error(message, "Помилка: Рядок не відповідає формату DD-MM-YYYY")
            return
        await form_set_value(state, TAG_IMPACT_FORM, "day", valid_date)
    elif field_name == "tag":
        await form_set_value(state, TAG_IMPACT_FORM, "tag", message.text)

    text = await render_upsert_impact(state)

    await refresh_form_message(
        text=text,
        state=state,
        bot=bot,
        form_name=TAG_IMPACT_FORM,
        mapping=tag_impact_mapping
    )

    await finish_text_input(state, message, TAG_IMPACT_FORM)

async def render_upsert_impact(state: FSMContext) -> str:
    form: TGForm = await form_get(state, TAG_IMPACT_FORM)

    impact_data = {tag: form["values"].get(tag, "—") for tag in tag_impact_mapping.keys()}
    day = form["values"].get("day", "—")
    text = f"📋 **Запис про вплив на настрій за {day}**\n\n" if day != "—" else "Запис про вплив на настрій за не вказаний день\n"
    text += "\n".join(f'{tag_impact_mapping.get(k).capitalize()}: {v}' for k ,v in impact_data.items())

    return text

@router.message(F.text == CommonMoodMenu.BTN_UPSERT_TAG_IMPACT_FOR_DAY)
async def show_tag_impact_data(message: types.Message, state: FSMContext):
    text = await render_upsert_impact(state)

    sent_message = await message.answer(text, reply_markup=get_form_keyboard(tag_impact_mapping, TAG_IMPACT_FORM), parse_mode="Markdown")

    await form_set_last_msg(
        state=state,
        form_name=TAG_IMPACT_FORM,
        chat_id=sent_message.chat.id,
        message_id=sent_message.message_id
    )

    await state.set_state(TagImpactForm.waiting_input)