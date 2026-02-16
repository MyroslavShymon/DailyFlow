from aiogram import F
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from daily_flow.ui.telegram.keyboards.common_mood import CommonMoodMenu
from daily_flow.ui.telegram.runtime import router
from daily_flow.ui.telegram.keyboards.main import MainMenu
from daily_flow.ui.telegram.keyboards.mood import MoodMenu


@router.message(StateFilter(None), F.text == MainMenu.BTN_MOOD)
async def mood(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
        "Що саме ти хочеш зробити з емоціями:",
        reply_markup=MoodMenu.get()
    )

@router.message(StateFilter(None), F.text == MainMenu.BTN_COMMON_MOOD)
async def common_mood(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
        "Що саме ти хочеш зробити з настроєм:",
        reply_markup=CommonMoodMenu.get()
    )

@router.message(StateFilter(None), Command("start"))
async def start(message: Message):
    await message.answer(
        "Вітаю! Я твій щоденник. Оберіть з чим ми працюємо:",
        reply_markup=MainMenu.get()
    )
