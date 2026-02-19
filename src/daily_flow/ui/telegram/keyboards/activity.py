from aiogram.utils.keyboard import ReplyKeyboardBuilder

from daily_flow.ui.telegram.keyboards.main import MainMenu


class ActivityMenu:
    BTN_ADD_EDIT_ACTIVITY = "✨ Створити / редагувати активність"
    BTN_GET_ALL_ACTIVITIES = "📚 Переглянути всі активності"
    BTN_GET_ACTIVITY = "🔎 Знайти активність за ID"
    BTN_GET_ACTIVITIES_BY_CATEGORY = "📌 Переглянути активності за категорією"
    BTN_DELETE_ACTIVITY = "🗑️ Видалити активність"

    BTN_ADD_EDIT_CATEGORY = "🏷️ Створити / редагувати категорію"
    BTN_GET_ALL_CATEGORIES = "🗂️ Переглянути всі категорії"
    BTN_DELETE_CATEGORY = "🗑️ Видалити категорію"

    BTN_ASSIGN_CATEGORY_TO_ACTIVITY = "🔗 Додати категорію до активності"
    BTN_DELETE_CATEGORY_FROM_ACTIVITY = "❌ Прибрати категорію з активності"
    BTN_GET_CATEGORIES_BY_ACTIVITY = "🏷️ Переглянути категорії, які містить активність"
    BTN_GET_ACTIVITIES_BY_CATEGORY_LINK = "🎯 Переглянути активності, які містить категорія"

    BTN_ADD_EDIT_ACTIVITY_USAGE = "📌 Записати виконання активності"
    BTN_GET_USAGES_BY_ACTIVITY = "📈 Історія виконань активності"
    BTN_GET_USAGE_BY_ID = "🔎 Знайти запис виконання за ID"
    BTN_GET_LAST_USAGES = "🕒 Останні виконання"
    BTN_GET_USAGES_BY_PERIOD = "📅 Виконання за період"
    BTN_DELETE_USAGE = "🗑️ Видалити запис виконання"
    BTN_DELETE_USAGES_BY_ACTIVITY = "🧹 Очистити історію активності"

    @classmethod
    def get(cls):
        builder = ReplyKeyboardBuilder()

        builder.button(text=cls.BTN_ADD_EDIT_ACTIVITY)
        builder.button(text=cls.BTN_GET_ALL_ACTIVITIES)
        builder.button(text=cls.BTN_GET_ACTIVITY)
        builder.button(text=cls.BTN_GET_ACTIVITIES_BY_CATEGORY)
        builder.button(text=cls.BTN_DELETE_ACTIVITY)

        builder.button(text=cls.BTN_ADD_EDIT_CATEGORY)
        builder.button(text=cls.BTN_GET_ALL_CATEGORIES)
        builder.button(text=cls.BTN_DELETE_CATEGORY)

        builder.button(text=cls.BTN_ASSIGN_CATEGORY_TO_ACTIVITY)
        builder.button(text=cls.BTN_DELETE_CATEGORY_FROM_ACTIVITY)
        builder.button(text=cls.BTN_GET_CATEGORIES_BY_ACTIVITY)
        builder.button(text=cls.BTN_GET_ACTIVITIES_BY_CATEGORY_LINK)

        builder.button(text=cls.BTN_ADD_EDIT_ACTIVITY_USAGE)
        builder.button(text=cls.BTN_GET_USAGES_BY_ACTIVITY)
        builder.button(text=cls.BTN_GET_USAGE_BY_ID)
        builder.button(text=cls.BTN_GET_LAST_USAGES)
        builder.button(text=cls.BTN_GET_USAGES_BY_PERIOD)
        builder.button(text=cls.BTN_DELETE_USAGE)
        builder.button(text=cls.BTN_DELETE_USAGES_BY_ACTIVITY)

        builder.button(text=MainMenu.BTN_MENU)

        builder.adjust(1)
        return builder.as_markup(resize_keyboard=True)
