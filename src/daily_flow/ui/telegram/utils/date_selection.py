import re
from datetime import datetime, timedelta
from enum import StrEnum
from typing import Any

from aiogram import types
from aiogram.utils.keyboard import InlineKeyboardBuilder

from daily_flow.ui.telegram.utils.payload import pack_optional


class DateAction(StrEnum):
    GET = "get"
    DELETE = "delete"

DATE_PATTERN = re.compile(r"^\d{2}[-.]\d{2}[-.]\d{4}$")

def get_date_keyboard(
        action: DateAction,
        entity: str,
        optional_fields=None
):
    builder = InlineKeyboardBuilder()
    today = datetime.now()
    yesterday = today - timedelta(days=1)

    opt = pack_optional(optional_fields)

    def mk(date_val: str) -> str:
        return f"date_{entity}:{action}:{date_val}###{opt}"

    builder.button(
        text=f"Сьогодні ({today.strftime('%d.%m')})",
        callback_data=mk(today.strftime("%d-%m-%Y"))
    )
    builder.button(
        text=f"Вчора ({yesterday.strftime('%d.%m')})",
        callback_data=mk(yesterday.strftime("%d-%m-%Y"))
    )
    builder.button(
        text="Ввести вручну ✍️",
        callback_data=mk("manual")
    )

    builder.adjust(2)

    builder.row(
        types.InlineKeyboardButton(
            text="❌ Скасувати",
            callback_data="cancel_action"
        )
    )

    return builder.as_markup()
