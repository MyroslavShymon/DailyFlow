import re
from datetime import datetime, timedelta
from enum import StrEnum

from aiogram import types
from aiogram.utils.keyboard import InlineKeyboardBuilder


class DateAction(StrEnum):
    GET = "get"
    DELETE = "delete"

DATE_PATTERN = re.compile(r"^\d{2}[-.]\d{2}[-.]\d{4}$")

def get_date_keyboard(action: DateAction, state: str):
    builder = InlineKeyboardBuilder()
    today = datetime.now()
    yesterday = today - timedelta(days=1)

    builder.button(
        text=f"Сьогодні ({today.strftime('%d.%m')})",
        callback_data=f"date_{state}:{action}:{today.strftime('%d-%m-%Y')}"
    )
    builder.button(
        text=f"Вчора ({yesterday.strftime('%d.%m')})",
        callback_data=f"date_{state}:{action}:{yesterday.strftime('%d-%m-%Y')}"
    )
    builder.button(
        text="Ввести вручну ✍️",
        callback_data=f"date_{state}:{action}:manual"
    )

    builder.adjust(2)

    builder.row(
        types.InlineKeyboardButton(
            text="❌ Скасувати",
            callback_data="cancel_action"
        )
    )

    return builder.as_markup()
