import logging
from sqlalchemy.exc import SQLAlchemyError

from daily_flow.db.errors import (
    DuplicateError,
    MissingRequiredFieldError,
    UnknownFieldError,
    InvalidScoreError,
    DBIntegrityError,
    RepoError,
)
from daily_flow.db.repositories.activity.activity_repo import ActivityRepo, Activity
from daily_flow.services.activity.activity.dto import UpsertActivityDTO
from daily_flow.services.errors import ConflictError, UserInputError, TemporaryError

logger = logging.getLogger(__name__)

class ActivityService:
    def __init__(self, repo: ActivityRepo) -> None:
        self._repo = repo

    def upsert_activity(self, dto: UpsertActivityDTO) -> Activity:
        payload = dto.model_dump(exclude_none=True)

        title = payload.pop("title")
        values = payload

        try:
            return self._repo.upsert_activity(title=title, payload=values)
        except DuplicateError as e:
            raise ConflictError(str(e)) from e
        except (MissingRequiredFieldError, UnknownFieldError, InvalidScoreError) as e:
            raise UserInputError(str(e)) from e
        except (DBIntegrityError, RepoError) as e:
            logger.exception("ActivityService.upsert_activity failed (title=%s)", title)
            raise TemporaryError("Database error. Please try again.") from e

    def delete_activity_by_title(self, title: str) -> int:
        title = (title or "").strip()
        if not title:
            raise UserInputError("Please provide a correct title format")

        try:
            return self._repo.delete_activity_by_title(title=title)
        except (RepoError, SQLAlchemyError) as e:
            raise TemporaryError("Database error. Please try again.") from e

    def delete_activity_by_id(self, activity_id: int) -> int:
        if not activity_id:
            raise UserInputError("Please provide activity_id")

        try:
            return self._repo.delete_activity_by_id(activity_id=activity_id)
        except (RepoError, SQLAlchemyError) as e:
            raise TemporaryError("Database error. Please try again.") from e

    def get_activity_by_id(self, activity_id: int) -> Activity | None:
        if not activity_id:
            raise UserInputError("Please provide activity_id")

        try:
            return self._repo.get_activity_by_id(activity_id)
        except (RepoError, SQLAlchemyError) as e:
            raise TemporaryError("Database error. Please try again.") from e

    def get_activity_by_title(self, title: str) -> Activity | None:
        title = (title or "").strip()
        if not title:
            raise UserInputError("Please provide a correct title format")

        try:
            return self._repo.get_activity_by_title(title)
        except (RepoError, SQLAlchemyError) as e:
            raise TemporaryError("Database error. Please try again.") from e

    def get_all_activities(self) -> list[Activity]:
        try:
            return self._repo.get_all_activities()
        except (RepoError, SQLAlchemyError) as e:
            raise TemporaryError("Database error. Please try again.") from e

    def get_activities_by_category(self, category_id: int) -> list[Activity]:
        if not category_id:
            raise UserInputError("Please provide category_id")

        try:
            return self._repo.get_activities_by_category(category_id)
        except (RepoError, SQLAlchemyError) as e:
            raise TemporaryError("Database error. Please try again.") from e
