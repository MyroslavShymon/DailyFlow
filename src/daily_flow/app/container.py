from dataclasses import dataclass
from sqlalchemy.engine import Engine

from daily_flow.config.db import DbSettings
from daily_flow.db.engine import build_engine
from daily_flow.db.init import init_db
from daily_flow.db.repositories.common_mood_repo import CommonMoodLogRepo
from daily_flow.db.repositories.idea_repo import IdeaRepo
from daily_flow.db.repositories.mood_log_repo import MoodLogRepo
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

    mood_log_service: MoodLogService
    common_mood_log_service: CommonMoodLogService
    idea_service: IdeaService

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

    mood_log_service = MoodLogService(repo=mood_log_repo)
    common_mood_log_service = CommonMoodLogService(repo=common_mood_log_repo)
    idea_service = IdeaService(repo=idea_repo)

    return Container(
        db_settings=db_settings,
        engine=engine,

        mood_log_repo=mood_log_repo,
        common_mood_log_repo=common_mood_log_repo,
        idea_repo=idea_repo,

        mood_log_service=mood_log_service,
        common_mood_log_service=common_mood_log_service,
        idea_service=idea_service
    )