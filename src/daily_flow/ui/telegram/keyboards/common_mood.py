from aiogram.utils.keyboard import ReplyKeyboardBuilder

from daily_flow.ui.telegram.keyboards.main import MainMenu


class CommonMoodMenu:
    BTN_ADD_EDIT_COMMON_MOOD_LOG = "✨ Оновити стан дня"
    BTN_GET_COMMON_MOOD_LOG = "📖 Щоденник настрою"
    BTN_UPSERT_TAG_IMPACT_FOR_DAY = "⚡ Що вплинуло на стан?"
    BTN_GET_ALL_TAGS = "🗂️ Список усіх тегів"
    BTN_GET_TAGS_BY_DAY = "📅 Події за день"
    BTN_DELETE_TAG_BY_DAY = "🗑️ Видалити теги дня"

    @classmethod
    def get(cls):
        builder = ReplyKeyboardBuilder()
        builder.button(text=cls.BTN_ADD_EDIT_COMMON_MOOD_LOG)
        builder.button(text=cls.BTN_GET_COMMON_MOOD_LOG)
        builder.button(text=cls.BTN_UPSERT_TAG_IMPACT_FOR_DAY)
        builder.button(text=cls.BTN_GET_ALL_TAGS)
        builder.button(text=cls.BTN_GET_TAGS_BY_DAY)
        builder.button(text=cls.BTN_DELETE_TAG_BY_DAY)
        builder.button(text=MainMenu.BTN_MENU)
        builder.adjust(1)
        return builder.as_markup(resize_keyboard=True)
