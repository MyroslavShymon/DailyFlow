import logging
from sqlalchemy.exc import SQLAlchemyError

from daily_flow.db.errors import MissingRequiredFieldError, DuplicateError, DBIntegrityError, RepoError, \
    UnknownFieldError, ParentNotFoundError
from daily_flow.db.repositories.idea_repo import IdeaRepo, Sphere, Idea
from daily_flow.services.errors import ConflictError, UserInputError, TemporaryError
from daily_flow.services.idea.dto import UpsertSphereDTO, UpsertIdeaDTO, SphereToIdeaDTO

logger = logging.getLogger(__name__)

class IdeaService:
    def __init__(self, repo: IdeaRepo) -> None:
        self._repo = repo

    def upsert_sphere(self, dto: UpsertSphereDTO) -> Sphere:
        payload = dto.model_dump(exclude_none=True)

        name = payload.pop("name")
        description = payload.pop("description", None)

        try:
            sphere = self._repo.upsert_sphere(
                name=name,
                description=description
            )

            return sphere
        except DuplicateError as e:
            raise ConflictError(str(e)) from e
        except MissingRequiredFieldError as e:
            raise UserInputError(str(e)) from e
        except (DBIntegrityError, RepoError) as e:
            logger.exception(
                "IdeaService.upsert_sphere failed (name=%s)",
                name,
            )
            raise TemporaryError("Database error. Please try again.") from e

    def upsert_idea(self, dto: UpsertIdeaDTO) -> Idea:
        payload = dto.model_dump(exclude_none=True)

        title = payload.pop("title")
        values = payload

        try:
            idea = self._repo.upsert_idea(
                title=title,
                payload=values
            )
            return idea
        except DuplicateError as e:
            raise ConflictError(str(e)) from e
        except (MissingRequiredFieldError, UnknownFieldError) as e:
            raise UserInputError(str(e)) from e
        except (DBIntegrityError, RepoError) as e:
            logger.exception(
                "IdeaService.upsert_idea failed (title=%s)",
                title,
            )
            raise TemporaryError("Database error. Please try again.") from e

    def assign_sphere_to_idea(self, dto: SphereToIdeaDTO) -> bool:
        sphere_id, idea_id = dto.sphere_id, dto.idea_id
        try:
            return self._repo.assign_sphere_to_idea(sphere_id=sphere_id, idea_id=idea_id)
        except ParentNotFoundError as e:
            raise UserInputError(str(e)) from e
        except (DBIntegrityError, RepoError) as e:
            logger.exception(
                "IdeaService.assign_sphere_to_idea failed (sphere_id=%s, idea_id=%s)",
                sphere_id,
                idea_id
            )
            raise TemporaryError("Database error. Please try again.") from e

    def delete_idea_by_title(self, title: str) -> int:
        title = (title or "").strip()
        if not title:
            raise UserInputError("Please provide a correct title format")

        try:
            return self._repo.delete_idea_by_title(title=title)
        except (RepoError, SQLAlchemyError) as e:
            raise TemporaryError("Database error. Please try again.") from e

    def delete_sphere_from_idea(self, dto: SphereToIdeaDTO) -> int:
        sphere_id, idea_id = dto.sphere_id, dto.idea_id
        try:
            return self._repo.delete_sphere_from_idea(idea_id=idea_id, sphere_id=sphere_id)
        except ParentNotFoundError as e:
            raise UserInputError(str(e)) from e
        except (RepoError, SQLAlchemyError) as e:
            raise TemporaryError("Database error. Please try again.") from e

    def delete_sphere_by_name(self, name: str) -> int:
        name = (name or "").strip()
        if not name:
            raise UserInputError("Please provide a correct sphere name format")

        try:
            return self._repo.delete_sphere_by_name(name=name)
        except (RepoError, SQLAlchemyError) as e:
            raise TemporaryError("Database error. Please try again.") from e

    def get_ideas_by_sphere(self, sphere_id: int) -> list[Idea]:
        try:
            return self._repo.get_ideas_by_sphere(sphere_id)
        except (RepoError, SQLAlchemyError) as e:
            raise TemporaryError("Database error. Please try again.") from e

    def get_all_ideas(self) -> list[Idea]:
        try:
            return self._repo.get_all_ideas()
        except (RepoError, SQLAlchemyError) as e:
            raise TemporaryError("Database error. Please try again.") from e


    def get_all_spheres(self) -> list[Sphere]:
        try:
            return self._repo.get_all_spheres()
        except (RepoError, SQLAlchemyError) as e:
            raise TemporaryError("Database error. Please try again.") from e