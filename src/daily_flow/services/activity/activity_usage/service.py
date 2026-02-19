import logging
from sqlalchemy.exc import SQLAlchemyError

from daily_flow.db.errors import (
    DuplicateError,
    MissingRequiredFieldError,
    UnknownFieldError,
    InvalidScoreError,
    ParentNotFoundError,
    DBIntegrityError,
    RepoError,
)
from daily_flow.db.repositories.activity.activity_usage_repo import ActivityUsageRepo, ActivityUsage
from daily_flow.services.activity.activity_usage.dto import UpsertActivityUsageDTO, ActivityUsagePeriodDTO
from daily_flow.services.errors import ConflictError, UserInputError, TemporaryError

logger = logging.getLogger(__name__)

class ActivityUsageService:
    def __init__(self, repo: ActivityUsageRepo) -> None:
        self._repo = repo

    def upsert_activity_usage(self, dto: UpsertActivityUsageDTO) -> ActivityUsage:
        payload = dto.model_dump(exclude_none=True)

        usage_id = payload.pop("usage_id", None)
        activity_id = payload.pop("activity_id")
        used_at = payload.pop("used_at")

        values = payload

        try:
            return self._repo.upsert_activity_usage(
                activity_id=activity_id,
                used_at=used_at,
                payload=values,
                usage_id=usage_id,
            )
        except DuplicateError as e:
            raise ConflictError(str(e)) from e
        except (MissingRequiredFieldError, UnknownFieldError, InvalidScoreError, ParentNotFoundError) as e:
            raise UserInputError(str(e)) from e
        except (DBIntegrityError, RepoError) as e:
            logger.exception(
                "ActivityUsageService.upsert_activity_usage failed (usage_id=%s, activity_id=%s, used_at=%s)",
                usage_id,
                activity_id,
                str(used_at),
            )
            raise TemporaryError("Database error. Please try again.") from e

    def delete_activity_usage_by_id(self, usage_id: int) -> int:
        if not usage_id:
            raise UserInputError("Please provide usage_id")

        try:
            return self._repo.delete_activity_usage_by_id(usage_id)
        except (RepoError, SQLAlchemyError) as e:
            raise TemporaryError("Database error. Please try again.") from e

    def delete_activity_usages_by_activity(self, activity_id: int) -> int:
        if not activity_id:
            raise UserInputError("Please provide activity_id")

        try:
            return self._repo.delete_activity_usages_by_activity(activity_id)
        except (RepoError, SQLAlchemyError) as e:
            raise TemporaryError("Database error. Please try again.") from e

    def get_activity_usage_by_id(self, usage_id: int) -> ActivityUsage | None:
        if not usage_id:
            raise UserInputError("Please provide usage_id")

        try:
            return self._repo.get_activity_usage_by_id(usage_id)
        except (RepoError, SQLAlchemyError) as e:
            raise TemporaryError("Database error. Please try again.") from e

    def get_activity_usages_by_activity(self, activity_id: int) -> list[ActivityUsage]:
        if not activity_id:
            raise UserInputError("Please provide activity_id")

        try:
            return self._repo.get_activity_usages_by_activity(activity_id)
        except (RepoError, SQLAlchemyError) as e:
            raise TemporaryError("Database error. Please try again.") from e

    def get_activity_usages_by_period(self, dto: ActivityUsagePeriodDTO) -> list[ActivityUsage]:
        payload = dto.model_dump()
        date_from = payload["date_from"]
        date_to = payload["date_to"]

        try:
            return self._repo.get_activity_usages_by_period(date_from, date_to)
        except (MissingRequiredFieldError, RepoError, SQLAlchemyError) as e:
            raise TemporaryError("Database error. Please try again.") from e

    def get_last_activity_usages(self, limit: int) -> list[ActivityUsage]:
        if not limit or limit <= 0:
            raise UserInputError("limit must be > 0")

        try:
            return self._repo.get_last_activity_usages(limit)
        except (MissingRequiredFieldError, RepoError, SQLAlchemyError) as e:
            raise TemporaryError("Database error. Please try again.") from e
