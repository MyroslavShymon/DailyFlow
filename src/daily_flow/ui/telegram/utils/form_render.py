from aiogram.utils.keyboard import InlineKeyboardBuilder, InlineKeyboardMarkup
from aiogram import types

def get_form_keyboard(mapping: dict[str, str], form: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for item, item_translated in mapping.items():
        builder.row(types.InlineKeyboardButton(text=f"Введіть дані про {item_translated}", callback_data=f"edit_{form}:{item}"))
    builder.row(types.InlineKeyboardButton(text="✅ Все вірно", callback_data=f"submit_{form}_form"))
    return builder.as_markup()