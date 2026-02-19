import logging
from sqlalchemy.exc import SQLAlchemyError

from daily_flow.db.errors import DuplicateError, MissingRequiredFieldError, DBIntegrityError, RepoError
from daily_flow.db.repositories.activity.category_repo import CategoryRepo, Category
from daily_flow.services.activity.category.dto import UpsertCategoryDTO
from daily_flow.services.errors import ConflictError, UserInputError, TemporaryError

logger = logging.getLogger(__name__)

class CategoryService:
    def __init__(self, repo: CategoryRepo) -> None:
        self._repo = repo

    def upsert_category(self, dto: UpsertCategoryDTO) -> Category:
        payload = dto.model_dump(exclude_none=True)

        name = payload.pop("name")
        description = payload.pop("description", None)

        try:
            return self._repo.upsert_category(name=name, description=description)
        except DuplicateError as e:
            raise ConflictError(str(e)) from e
        except MissingRequiredFieldError as e:
            raise UserInputError(str(e)) from e
        except (DBIntegrityError, RepoError) as e:
            logger.exception("CategoryService.upsert_category failed (name=%s)", name)
            raise TemporaryError("Database error. Please try again.") from e

    def delete_category_by_name(self, name: str) -> int:
        name = (name or "").strip()
        if not name:
            raise UserInputError("Please provide a correct name format")

        try:
            return self._repo.delete_category_by_name(name=name)
        except (RepoError, SQLAlchemyError) as e:
            raise TemporaryError("Database error. Please try again.") from e

    def delete_category_by_id(self, category_id: int) -> int:
        if not category_id:
            raise UserInputError("Please provide category_id")

        try:
            return self._repo.delete_category_by_id(category_id=category_id)
        except (RepoError, SQLAlchemyError) as e:
            raise TemporaryError("Database error. Please try again.") from e

    def get_category_by_id(self, category_id: int) -> Category | None:
        if not category_id:
            raise UserInputError("Please provide category_id")

        try:
            return self._repo.get_category_by_id(category_id)
        except (RepoError, SQLAlchemyError) as e:
            raise TemporaryError("Database error. Please try again.") from e

    def get_category_by_name(self, name: str) -> Category | None:
        name = (name or "").strip()
        if not name:
            raise UserInputError("Please provide a correct name format")

        try:
            return self._repo.get_category_by_name(name)
        except (RepoError, SQLAlchemyError) as e:
            raise TemporaryError("Database error. Please try again.") from e

    def get_all_categories(self) -> list[Category]:
        try:
            return self._repo.get_all_categories()
        except (RepoError, SQLAlchemyError) as e:
            raise TemporaryError("Database error. Please try again.") from e
