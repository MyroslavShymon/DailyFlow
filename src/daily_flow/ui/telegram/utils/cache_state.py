from typing import TypedDict

from aiogram.fsm.context import FSMContext

CACHE_KEY = "cache"

class TGCache(TypedDict):
    tags: list[str] | None

async def get_cache(state: FSMContext) -> TGCache:
    data = await state.get_data()
    return data.get(CACHE_KEY, {})

async def set_cache_field(state: FSMContext, key: str, value):
    data = await state.get_data()
    cache = data.get(CACHE_KEY, {})
    cache[key] = value
    await state.update_data({CACHE_KEY: cache})

