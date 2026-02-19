from aiogram.fsm.state import StatesGroup, State

class TagImpactForm(StatesGroup):
    waiting_input = State()

class CommonMoodLogForm(StatesGroup):
    waiting_input = State()

class MoodLogForm(StatesGroup):
    waiting_input = State()

class IdeaForm(StatesGroup):
    waiting_input = State()

class SphereForm(StatesGroup):
    waiting_input = State()

class SphereToIdeaAssignForm(StatesGroup):
    waiting_for_idea_id = State()
    waiting_for_sphere_id = State()

class SphereToIdeaDeleteForm(StatesGroup):
    waiting_for_idea_id = State()
    waiting_for_sphere_id = State()

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

class IdeaDeleteForm(StatesGroup):
    waiting_for_title = State()

class SphereDeleteForm(StatesGroup):
    waiting_for_name = State()

class IdeaBySphereGetForm(StatesGroup):
    waiting_for_sphere_id = State()

class ActivityForm(StatesGroup):
    waiting_input = State()

class CategoryForm(StatesGroup):
    waiting_input = State()

class ActivityCategoryForm(StatesGroup):
    waiting_input = State()

class ActivityUsageForm(StatesGroup):
    waiting_input = State()

class ActivityGetForm(StatesGroup):
    waiting_for_ref = State()

class ActivityByCategoryGetForm(StatesGroup):
    waiting_for_category_id = State()

class ActivityDeleteForm(StatesGroup):
    waiting_for_ref = State()

class CategoryDeleteForm(StatesGroup):
    waiting_for_ref = State()

class ActivityCategoryAssignDeleteForm(StatesGroup):
    waiting_for_activity_id = State()
    waiting_for_category_id = State()

class ActivityCategoryGetCategoriesForm(StatesGroup):
    waiting_for_activity_id = State()

class ActivityCategoryGetActivitiesForm(StatesGroup):
    waiting_for_category_id = State()

class ActivityUsageGetByIdForm(StatesGroup):
    waiting_for_usage_id = State()

class ActivityUsageGetByActivityForm(StatesGroup):
    waiting_for_activity_id = State()

class ActivityUsageLastForm(StatesGroup):
    waiting_for_limit = State()

class ActivityUsagePeriodForm(StatesGroup):
    waiting_for_date_from = State()
    waiting_for_date_to = State()

class ActivityUsageDeleteForm(StatesGroup):
    waiting_for_usage_id = State()

class ActivityUsageDeleteByActivityForm(StatesGroup):
    waiting_for_activity_id = State()