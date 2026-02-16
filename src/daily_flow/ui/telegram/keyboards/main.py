from aiogram.utils.keyboard import ReplyKeyboardBuilder


class MainMenu:
    BTN_COMMON_MOOD = "📝 З настроєм"
    BTN_MOOD = "❤️ З емоціями"
    BTN_IDEAS = "💡 З ідеями"
    BTN_MENU = "🏠 Меню"

    @classmethod
    def get(cls):
        builder = ReplyKeyboardBuilder()
        builder.button(text=cls.BTN_COMMON_MOOD)
        builder.button(text=cls.BTN_MOOD)
        builder.button(text=cls.BTN_IDEAS)
        builder.button(text=cls.BTN_MENU)
        builder.adjust(2, 1)
        return builder.as_markup(resize_keyboard=True)
