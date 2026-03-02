from aiogram.utils.keyboard import ReplyKeyboardBuilder

from daily_flow.ui.telegram.keyboards.main import MainMenu


class MoodMenu:
    BTN_ADD_EDIT_MOOD_LOG = "✍️ Додати або редагувати емоції"
    BTN_GET_MOOD_LOG = "🔍 Переглянути запис по емоціях"
    BTN_DELETE_MOOD_LOG = "🗑️ Видалити запис про емоції"

    @classmethod
    def get(cls):
        builder = ReplyKeyboardBuilder()
        builder.button(text=cls.BTN_ADD_EDIT_MOOD_LOG)
        builder.button(text=cls.BTN_GET_MOOD_LOG)
        builder.button(text=cls.BTN_DELETE_MOOD_LOG)
        builder.button(text=MainMenu.BTN_MENU)
        builder.adjust(1)
        return builder.as_markup(resize_keyboard=True)
