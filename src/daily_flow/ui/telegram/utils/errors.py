import asyncio
from aiogram import types


async def handle_message_error(message: types.Message, text: str):
    error_msg = await message.answer(text)
    await asyncio.sleep(3)
    await error_msg.delete()