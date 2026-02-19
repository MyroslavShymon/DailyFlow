from dataclasses import dataclass
from sqlalchemy.engine import Engine

from daily_flow.config.db import DbSettings
from daily_flow.db.engine import build_engine
from daily_flow.db.init import init_db
from daily_flow.db.repositories.activity.activity_category_repo import ActivityCategoryRepo
from daily_flow.db.repositories.activity.activity_repo import ActivityRepo
from daily_flow.db.repositories.activity.activity_usage_repo import ActivityUsageRepo
from daily_flow.db.repositories.activity.category_repo import CategoryRepo
from daily_flow.db.repositories.common_mood_repo import CommonMoodLogRepo
from daily_flow.db.repositories.idea_repo import IdeaRepo
from daily_flow.db.repositories.mood_log_repo import MoodLogRepo
from daily_flow.services.activity.activity.service import ActivityService
from daily_flow.services.activity.activity_category.service import ActivityCategoryService
from daily_flow.services.activity.activity_usage.service import ActivityUsageService
from daily_flow.services.activity.category.service import CategoryService
from daily_flow.services.common_mood.service import CommonMoodLogService
from daily_flow.services.idea.service import IdeaService
from daily_flow.services.mood_log.service import MoodLogService

@dataclass(frozen=True)
class Container:
    db_settings: DbSettings
    engine: Engine

    mood_log_repo: MoodLogRepo
    common_mood_log_repo: CommonMoodLogRepo
    idea_repo: IdeaRepo
    activity_repo: ActivityRepo
    category_repo: CategoryRepo
    activity_category_repo: ActivityCategoryRepo
    activity_usage_repo: ActivityUsageRepo

    mood_log_service: MoodLogService
    common_mood_log_service: CommonMoodLogService
    idea_service: IdeaService
    activity_service: ActivityService
    category_service: CategoryService
    activity_category_service: ActivityCategoryService
    activity_usage_service: ActivityUsageService

def build_container(db_settings: DbSettings) -> Container:
    engine = build_engine(
        database_url=db_settings.db_url,
        is_database_echo=db_settings.is_sql_echo
    )

    if db_settings.auto_init_db:
        init_db(engine)

    mood_log_repo = MoodLogRepo(engine)
    common_mood_log_repo = CommonMoodLogRepo(engine)
    idea_repo = IdeaRepo(engine)
    activity_repo = ActivityRepo(engine)
    category_repo = CategoryRepo(engine)
    activity_category_repo = ActivityCategoryRepo(engine)
    activity_usage_repo = ActivityUsageRepo(engine)

    mood_log_service = MoodLogService(repo=mood_log_repo)
    common_mood_log_service = CommonMoodLogService(repo=common_mood_log_repo)
    idea_service = IdeaService(repo=idea_repo)
    activity_service = ActivityService(repo=activity_repo)
    category_service = CategoryService(repo=category_repo)
    activity_category_service = ActivityCategoryService(repo=activity_category_repo)
    activity_usage_service = ActivityUsageService(repo=activity_usage_repo)

    return Container(
        db_settings=db_settings,
        engine=engine,

        mood_log_repo=mood_log_repo,
        common_mood_log_repo=common_mood_log_repo,
        idea_repo=idea_repo,
        activity_repo=activity_repo,
        category_repo=category_repo,
        activity_category_repo=activity_category_repo,
        activity_usage_repo=activity_usage_repo,

        mood_log_service=mood_log_service,
        common_mood_log_service=common_mood_log_service,
        idea_service=idea_service,
        activity_service=activity_service,
        category_service=category_service,
        activity_category_service=activity_category_service,
        activity_usage_service=activity_usage_service,
    )