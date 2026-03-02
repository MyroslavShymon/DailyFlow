from typing import Any, TypeVar

from aiogram import types
from pydantic import BaseModel, ValidationError

DTO = TypeVar("DTO", bound=BaseModel)


async def process_dto(
    callback: types.CallbackQuery,
    values: dict[str, Any],
    dto_class: type[DTO],
    mapping: dict[str, str],
) -> DTO | None:
    try:
        dto = dto_class(**values)
        return dto
    except ValidationError as e:
        err = e.errors()[0]
        field = err["loc"][0]
        msg = err["msg"]

        friendly_msg = f"Значення поля '{mapping.get(field)}' некоректне: {msg}"
        await callback.message.answer(f"❌ {friendly_msg}")
        return None
