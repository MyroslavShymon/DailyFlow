from aiogram.utils.keyboard import ReplyKeyboardBuilder

from daily_flow.ui.telegram.keyboards.main import MainMenu


class IdeaMenu:
    BTN_ADD_EDIT_IDEA = "✨ Додати/оновити ідею"
    BTN_GET_ALL_IDEAS = "📚 Список ідей"
    BTN_IDEAS_BY_SPHERE = "📌 Ідеї за сферою"
    BTN_DELETE_IDEA = "🗑️ Видалити ідею"

    BTN_ASSIGN_SPHERE_TO_IDEA = "➕ Додати сферу до ідеї"
    BTN_DELETE_SPHERE_FROM_IDEA = "➖ Прибрати сферу з ідеї"

    BTN_ADD_EDIT_SPHERE = "🧭 Додати/оновити сферу"
    BTN_GET_ALL_SPHERES = "🗂️ Список сфер"
    BTN_DELETE_SPHERE = "🗑️ Видалити сферу"

    @classmethod
    def get(cls):
        builder = ReplyKeyboardBuilder()

        builder.button(text=cls.BTN_ADD_EDIT_IDEA)
        builder.button(text=cls.BTN_GET_ALL_IDEAS)
        builder.button(text=cls.BTN_IDEAS_BY_SPHERE)
        builder.button(text=cls.BTN_DELETE_IDEA)

        builder.button(text=cls.BTN_ASSIGN_SPHERE_TO_IDEA)
        builder.button(text=cls.BTN_DELETE_SPHERE_FROM_IDEA)

        builder.button(text=cls.BTN_ADD_EDIT_SPHERE)
        builder.button(text=cls.BTN_GET_ALL_SPHERES)
        builder.button(text=cls.BTN_DELETE_SPHERE)

        builder.button(text=MainMenu.BTN_MENU)

        builder.adjust(1)
        return builder.as_markup(resize_keyboard=True)
