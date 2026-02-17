from daily_flow.ui.telegram.keyboards.main import MainMenu
from daily_flow.ui.telegram.runtime import router

from aiogram import types, F
from aiogram.fsm.context import FSMContext
from aiogram.filters import StateFilter

@router.callback_query(F.data == "cancel_action", StateFilter("*"))
async def cancel_handler(callback: types.CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_reply_markup(reply_markup=None)

    await callback.message.answer(
        text="Дію скасовано. Повертаємось у головне меню.",
        reply_markup=MainMenu.get()
    )
    await callback.answer()

@router.message(StateFilter(None), F.text == MainMenu.BTN_MENU)
async def menu_handler(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer(
        text="Повертаємось до початкового меню.",
        reply_markup=MainMenu.get(),
    )