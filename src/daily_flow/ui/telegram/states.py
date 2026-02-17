from aiogram.fsm.state import StatesGroup, State

class TagImpactForm(StatesGroup):
    waiting_input = State()

class CommonMoodLogForm(StatesGroup):
    waiting_input = State()

class MoodLogForm(StatesGroup):
    waiting_input = State()

class CommonMoodGetForm(StatesGroup):
    waiting_for_date = State()

class TagImpactGetForm(StatesGroup):
    waiting_for_date = State()

class TagImpactDeleteForm(StatesGroup):
    waiting_for_date = State()
    waiting_for_tag_name = State()

class MoodGetForm(StatesGroup):
    waiting_for_date = State()

class MoodDeleteForm(StatesGroup):
    waiting_for_date = State()