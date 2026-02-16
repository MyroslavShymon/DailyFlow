import logging
from datetime import date
from sqlalchemy.exc import SQLAlchemyError

from daily_flow.db.errors import DuplicateDayError, DuplicateError, MissingRequiredFieldError, InvalidScoreError, \
    UnknownFieldError, EmptyUpsertPayloadError, DBIntegrityError, RepoError, ParentNotFoundError
from daily_flow.db.repositories.common_mood_repo import CommonMoodLogRepo, CommonMoodLog, MoodTagImpact
from daily_flow.services.common_mood.dto import UpsertCommonMoodLogDTO, UpsertTagImpactDTO
from daily_flow.services.errors import UserInputError, ConflictError, TemporaryError

logger = logging.getLogger(__name__)

class CommonMoodLogService:
    def __init__(self, repo: CommonMoodLogRepo) -> None:
        self._repo = repo

    def upsert_common_mood_log(self, dto: UpsertCommonMoodLogDTO) -> CommonMoodLog:
        payload = dto.model_dump(exclude_none=True)

        day = payload.pop("day")
        values = payload

        if not values:
            raise UserInputError("Provide mood or note.")

        try:
            common_mood_log = self._repo.upsert_common_mood_log_by_day(
                day=day,
                payload=values
            )
            return common_mood_log
        except (DuplicateDayError, DuplicateError) as e:
            raise ConflictError(str(e)) from e
        except (MissingRequiredFieldError, InvalidScoreError, UnknownFieldError, EmptyUpsertPayloadError) as e:
            raise UserInputError(str(e)) from e
        # except ForeignKeyViolationError(поки не ясно як використовувати і чи треба саме для цієї схеми)
        except (DBIntegrityError, RepoError) as e:
            logger.exception(
                "CommonMoodService.upsert_common_mood_log failed (day=%s)",
                day,
            )
            raise TemporaryError("Database error. Please try again.") from e

    def get_common_mood_by_day(self, day: date) -> CommonMoodLog | None:
        if not day:
            raise UserInputError("Please provide a day param")

        try:
            return self._repo.get_common_mood_log_by_day(day)
        except (RepoError, SQLAlchemyError) as e:
            raise TemporaryError("Database error. Please try again.") from e

    def upsert_tag_impact_for_day(self, dto: UpsertTagImpactDTO) -> MoodTagImpact:
        payload = dto.model_dump(exclude_none=True)

        day = payload.pop("day")
        values = payload

        if not values:
            raise UserInputError("Provide tag and impact.")

        try:
            tag_impact = self._repo.upsert_tag_by_day(day=day, payload=values)
            return tag_impact
        except DuplicateError as e:
            raise ConflictError(str(e)) from e
        except (InvalidScoreError, UnknownFieldError, EmptyUpsertPayloadError, ParentNotFoundError, MissingRequiredFieldError) as e:
            raise UserInputError(str(e)) from e
        except (DBIntegrityError, RepoError) as e:
            logger.exception(
                "CommonMoodService.upsert_tag_impact_for_day failed (day=%s)",
                day,
            )
            raise TemporaryError("Database error. Please try again.") from e

    def get_tags_by_day(self, day: date) -> list[MoodTagImpact]:
        if not day:
            raise UserInputError("Please provide a day param")

        try:
            return self._repo.get_tags_by_day(day)
        except (RepoError, SQLAlchemyError) as e:
            raise TemporaryError("Database error. Please try again.") from e

    def delete_tag_by_day(self, day: date, tag: str) -> int:
        if not day or not tag:
            raise UserInputError("Please provide a day or tag params")

        try:
            return self._repo.delete_tag_by_day(day=day, tag=tag)
        except (MissingRequiredFieldError, ParentNotFoundError) as e:
            raise UserInputError(str(e)) from e
        except (RepoError, SQLAlchemyError) as e:
            raise TemporaryError("Database error. Please try again.") from e

    def get_all_unique_tags(self) -> list[str]:
        try:
            return self._repo.get_all_unique_tags()
        except (RepoError, SQLAlchemyError) as e:
            raise TemporaryError("Database error. Please try again.") from e
