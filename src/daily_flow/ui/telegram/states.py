from aiogram.fsm.state import StatesGroup, State

class CommonMoodLogForm(StatesGroup):
    last_chat_id = State()
    last_form_message_id = State()
    waiting_for_any_common_mood_input = State()
    current_editing_field = State()

class CommonMoodGetForm(StatesGroup):
    waiting_for_date = State()

class MoodLogForm(StatesGroup):
    waiting_for_any_mood_log_input = State()
    current_editing_field = State()

class MoodDeleteForm(StatesGroup):
    waiting_for_date = State()

class MoodGetForm(StatesGroup):
    waiting_for_date = State()