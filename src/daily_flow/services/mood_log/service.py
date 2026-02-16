import logging
from datetime import date
from sqlalchemy.exc import SQLAlchemyError

from daily_flow.db.errors import DuplicateError, DuplicateDayError, InvalidScoreError, DBIntegrityError, \
    EmptyUpsertPayloadError, UnknownFieldError, RepoError
from daily_flow.db.repositories.mood_log_repo import MoodLogRepo, MoodLog
from daily_flow.services.errors import ConflictError, UserInputError, TemporaryError, NotFoundError
from daily_flow.services.mood_log.dto import UpsertMoodLogDTO

logger = logging.getLogger(__name__)

class MoodLogService:
    def __init__(self, repo: MoodLogRepo) -> None:
        self._repo = repo

    def upsert_mood_log(self, dto: UpsertMoodLogDTO) -> MoodLog:
        payload = dto.model_dump(exclude_none=True)
        print(f"repo_payload{dto=}")
        day = payload.pop("day")
        values = payload

        if not values:
            raise UserInputError("Provide at least one score to save.")

        try:
            mood_log = self._repo.upsert_mood_log_by_day(
                day=day,
                values=values
            )
            return mood_log
        except (DuplicateDayError, DuplicateError) as e:
            raise ConflictError(str(e)) from e
        except (InvalidScoreError, UnknownFieldError, EmptyUpsertPayloadError) as e:
            raise UserInputError(str(e)) from e
        # except ForeignKeyViolationError(поки не ясно як використовувати і чи треба саме для цієї схеми)
        except (DBIntegrityError, RepoError) as e:
            logger.exception(
                "MoodLogService.upsert_mood_log failed (day=%s)",
                day,
            )
            raise TemporaryError("Database error. Please try again.") from e

    def get_mood_log_by_day(self, day: date) -> MoodLog | None:
        if not day:
            raise UserInputError("Please provide a day param")

        try:
            return self._repo.get_mood_log_by_day(day=day)
        except (RepoError, SQLAlchemyError) as e:
            raise TemporaryError("Database error. Please try again.") from e


    def get_list_by_date_range(self, start: date, end: date) -> list[MoodLog]:
        if None in (start, end):
            raise UserInputError("Please provide start or end day param")

        try:
            return self._repo.list_by_date_range(start=start, end=end)
        except (RepoError, SQLAlchemyError) as e:
            raise TemporaryError("Database error. Please try again.") from e


    def delete_mood_log_by_day(self, day: date) -> int:
        if not day:
            raise UserInputError("Please provide a day param")

        try:
            return self._repo.delete_mood_log_by_day(day)
        except (RepoError, SQLAlchemyError) as e:
            raise TemporaryError("Database error. Please try again.") from e


