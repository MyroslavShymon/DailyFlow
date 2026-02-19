import logging
from sqlalchemy.exc import SQLAlchemyError

from daily_flow.db.errors import ParentNotFoundError, DBIntegrityError, RepoError
from daily_flow.db.repositories.activity.activity_category_repo import ActivityCategoryRepo
from daily_flow.db.repositories.activity.activity_repo import Activity
from daily_flow.db.repositories.activity.category_repo import Category
from daily_flow.services.activity.activity_category.dto import CategoryToActivityDTO
from daily_flow.services.errors import UserInputError, TemporaryError

logger = logging.getLogger(__name__)

class ActivityCategoryService:
    def __init__(self, repo: ActivityCategoryRepo) -> None:
        self._repo = repo

    def assign_category_to_activity(self, dto: CategoryToActivityDTO) -> bool:
        category_id, activity_id = dto.category_id, dto.activity_id
        try:
            return self._repo.assign_category_to_activity(category_id=category_id, activity_id=activity_id)
        except ParentNotFoundError as e:
            raise UserInputError(str(e)) from e
        except (DBIntegrityError, RepoError) as e:
            logger.exception(
                "ActivityCategoryService.assign_category_to_activity failed (category_id=%s, activity_id=%s)",
                category_id,
                activity_id,
            )
            raise TemporaryError("Database error. Please try again.") from e

    def delete_category_from_activity(self, dto: CategoryToActivityDTO) -> int:
        category_id, activity_id = dto.category_id, dto.activity_id
        try:
            return self._repo.delete_category_from_activity(category_id=category_id, activity_id=activity_id)
        except ParentNotFoundError as e:
            raise UserInputError(str(e)) from e
        except (RepoError, SQLAlchemyError) as e:
            raise TemporaryError("Database error. Please try again.") from e

    def get_categories_by_activity(self, activity_id: int) -> list[Category]:
        if not activity_id:
            raise UserInputError("Please provide activity_id")

        try:
            return self._repo.get_categories_by_activity(activity_id)
        except (RepoError, SQLAlchemyError) as e:
            raise TemporaryError("Database error. Please try again.") from e

    def get_activities_by_category(self, category_id: int) -> list[Activity]:
        if not category_id:
            raise UserInputError("Please provide category_id")

        try:
            return self._repo.get_activities_by_category(category_id)
        except (RepoError, SQLAlchemyError) as e:
            raise TemporaryError("Database error. Please try again.") from e
