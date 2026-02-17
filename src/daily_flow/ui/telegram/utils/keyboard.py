from aiogram.utils.keyboard import InlineKeyboardBuilder


def build_inline_keyboard(
        field_name: str,
        button_names: list[str],
        start_index: int,
        button_adjusts: list[int],
):
    builder = InlineKeyboardBuilder()

    for i, label in enumerate(button_names, start=start_index):
        builder.button(text=label, callback_data=f"set_{field_name}_value:{i}")

    builder.adjust(*button_adjusts)
    return builder.as_markup()
