from typing import TypeVar, Type, Optional, Any
from pydantic import BaseModel, ValidationError
from aiogram import types

DTO = TypeVar("DTO", bound=BaseModel)

async def process_dto(
        callback: types.CallbackQuery,
        values: dict[str, Any],
        dto_class: Type[DTO],
        mapping: dict[str, str]
) -> Optional[DTO]:
    try:
        dto = dto_class(**values)
        return dto
    except ValidationError as e:
        err = e.errors()[0]
        field = err['loc'][0]
        msg = err['msg']

        friendly_msg = f"Значення поля '{mapping.get(field)}' некоректне: {msg}"
        await callback.message.answer(f"❌ {friendly_msg}")
        return None
