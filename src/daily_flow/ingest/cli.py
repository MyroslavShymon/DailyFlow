from dataclasses import dataclass
from pathlib import Path
from typing import Union

from sqlalchemy.engine import Engine

from daily_flow.config.db import DbSettings
from daily_flow.db.engine import build_engine
from daily_flow.db.init import init_db
from daily_flow.db.repositories.common_mood_repo import CommonMoodLogRepo
from daily_flow.db.repositories.ingest_run_repo import IngestRunRepo
from daily_flow.db.repositories.mood_log_repo import MoodLogRepo
from daily_flow.ingest.runner.common_mood_log import common_mood_log_runner
from daily_flow.ingest.runner.mood_log import mood_log_runner
from daily_flow.ingest.schemas.base import BaseIngestContract
from daily_flow.ingest.schemas.common_mood_log import CommonMoodLogIngestContract
from daily_flow.ingest.schemas.mood_log import MoodLogIngestContract 


@dataclass(frozen=True)
class IngestCLI:
    db_settings: DbSettings
    engine: Engine

    ingest_run_repo: IngestRunRepo

def build_ingest_cli(
        file_path: Union[str, Path],
        contract: BaseIngestContract,
        db_settings: DbSettings
) -> IngestCLI:
    engine = build_engine(
        database_url=db_settings.db_url,
        is_database_echo=db_settings.is_sql_echo
    )

    if db_settings.auto_init_db:
        init_db(engine)

    ingest_run_repo = IngestRunRepo(engine)

    if isinstance(contract, MoodLogIngestContract):
        mood_log_repo = MoodLogRepo(engine)

        mood_log_runner(
            file_path=file_path,
            contract=contract,
            ingest_run_repo=ingest_run_repo,
            mood_log_repo=mood_log_repo
        )

    if isinstance(contract, CommonMoodLogIngestContract):
        common_mood_log_repo = CommonMoodLogRepo(engine)

        common_mood_log_runner(
            file_path=file_path,
            contract=contract,
            ingest_run_repo=ingest_run_repo,
            common_mood_log_repo=common_mood_log_repo
        )

    return IngestCLI(
        db_settings=db_settings,
        engine=engine,
        ingest_run_repo=ingest_run_repo,
    )

