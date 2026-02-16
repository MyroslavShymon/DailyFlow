import logging
from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Mapping, Any
from enum import StrEnum

from sqlalchemy.engine import Engine, Result
from sqlalchemy.dialects.sqlite import insert as sqlite_insert
from sqlalchemy.exc import IntegrityError
from sqlalchemy import select, delete, exists, insert, and_

from daily_flow.db.errors import map_integrity_error, MissingRequiredFieldError, UnknownFieldError, ParentNotFoundError
from daily_flow.db.schema import idea, sphere, idea_sphere

logger = logging.getLogger(__name__)

ALLOWED_IDEA_FIELDS = {"description", "intent"}

class IdeaIntent(StrEnum):
    PROBLEM = "problem"
    SOLUTION = "solution"
    HYPOTHESIS = "hypothesis"
    QUESTION = "question"
    INSIGHT = "insight"
    TODO = "todo"

@dataclass(frozen=True)
class Idea:
    id: int
    title: str
    description: Optional[str]
    intent: Optional[IdeaIntent]
    created_at: datetime

@dataclass(frozen=True)
class Sphere:
    id: int
    name: str
    description: Optional[str]

class IdeaRepo:
    def __init__(self, engine: Engine) -> None:
        self._engine = engine

    @staticmethod
    def _to_idea(row_mapping: Mapping[str, Any]) -> Idea:
        return Idea(
            id=row_mapping["id"],
            title=row_mapping["title"],
            description=row_mapping["description"],
            intent=IdeaIntent(row_mapping["intent"]) if row_mapping["intent"] is not None else None,
            created_at=row_mapping["created_at"],
        )

    @staticmethod
    def _to_sphere(row_mapping: Mapping[str, Any]) -> Sphere:
        return Sphere(
            id=row_mapping["id"],
            name=row_mapping["name"],
            description=row_mapping["description"],
        )

    @staticmethod
    def _assert_exists(conn, table, entity_id: int, name: str) -> None:
        exists_row = conn.execute(
            select(exists().where(table.c.id == entity_id))
        ).scalar()

        if not exists_row:
            raise ParentNotFoundError(f"There is no {name} entity with such id")


    def upsert_sphere(
            self,
            name: str,
            description: str | None
    ) -> Sphere:
        name = (name or "").strip()
        if not name:
            raise MissingRequiredFieldError("Name param is empty to upsert.")

        insert_stmt = sqlite_insert(sphere).values(name=name, description=description)

        if description is None:
            stmt = (
                insert_stmt
                .on_conflict_do_nothing(index_elements=[sphere.c.name])
                .returning(*sphere.c)
            )
        else:
            stmt = (
                insert_stmt
                .on_conflict_do_update(
                    index_elements=[sphere.c.name],
                    set_={"description": description}
                )
                .returning(*sphere.c)
            )

        try:
            with self._engine.begin() as conn:
                res: Result = conn.execute(stmt)
                row = res.mappings().one_or_none()
                if row is None:
                    row = conn.execute(
                        select(sphere).where(sphere.c.name == name)
                    ).mappings().one()
                return self._to_sphere(row)
        except IntegrityError as e:
            logger.exception(
                "IdeaRepo.upsert_sphere failed "
                "(name=%s, description=%s)",
                name,
                description,
            )
            raise map_integrity_error(e, sphere.name) from e

    def upsert_idea(
            self,
            title: str,
            payload: dict[str, Any]
    ) -> Idea:
        title = (title or "").strip()
        if not title:
            raise MissingRequiredFieldError("Invalid format error for title field")
        unknown_keys = set(payload) - ALLOWED_IDEA_FIELDS
        if unknown_keys:
            raise UnknownFieldError(f"Unknown fields: {','.join(unknown_keys)}")

        insert_stmt = (
            sqlite_insert(idea)
            .values(title=title, **payload)
        )

        fields_to_update = {k: v for k, v in payload.items() if v is not None}
        if not fields_to_update:
            stmt = (
                insert_stmt
                .on_conflict_do_nothing(index_elements=[idea.c.title])
                .returning(*idea.c)
            )
        else:
            stmt = (
                insert_stmt
                .on_conflict_do_update(
                    index_elements=[idea.c.title],
                    set_=fields_to_update
                )
                .returning(*idea.c)
            )

        try:
            with self._engine.begin() as conn:
                res: Result = conn.execute(stmt)
                row = res.mappings().one_or_none()
                if row is None:
                    row = conn.execute(
                        select(idea)
                        .where(idea.c.title == title)
                    ).mappings().one()
                return self._to_idea(row)
        except IntegrityError as e:
            logger.exception(
                "IdeaRepo.upsert_idea failed "
                "(title=%s, fields=%s)",
                title,
                list(payload.keys()),
            )
            raise map_integrity_error(e, idea.name) from e

    def assign_sphere_to_idea(
            self,
            sphere_id: int,
            idea_id: int
    ) -> bool:
        try:
            with self._engine.begin() as conn:
                self._assert_exists(conn, idea, idea_id, "idea")
                self._assert_exists(conn, sphere, sphere_id, "sphere")

                stmt = (
                    sqlite_insert(idea_sphere)
                    .values(idea_id=idea_id, sphere_id=sphere_id)
                    .on_conflict_do_nothing(
                        index_elements=[idea_sphere.c.idea_id, idea_sphere.c.sphere_id]
                    )
                )
                res: Result = conn.execute(stmt)
                is_inserted = res.rowcount > 0
                return is_inserted
        except IntegrityError as e:
            logger.exception(
                "IdeaRepo.assign_sphere_to_idea failed "
                "(sphere_id=%s, idea_id=%s)",
                sphere_id,
                idea_id,
            )
            raise map_integrity_error(e, idea_sphere.name) from e


    def delete_idea_by_title(self, title: str) -> int:
        stmt = (
            delete(idea)
            .where(idea.c.title == title)
        )

        with self._engine.begin() as conn:
            res: Result = conn.execute(stmt)
            return int(res.rowcount or 0)

    def delete_sphere_from_idea(self, idea_id: int, sphere_id: int) -> int:
        with self._engine.begin() as conn:
            self._assert_exists(conn, idea, idea_id, "idea")
            self._assert_exists(conn, sphere, sphere_id, "sphere")
            stmt = (
                delete(idea_sphere)
                .where(
                    and_(
                        idea_sphere.c.idea_id == idea_id,
                        idea_sphere.c.sphere_id == sphere_id
                    )
                )
            )

            res: Result = conn.execute(stmt)
            return int(res.rowcount or 0)

    def get_ideas_by_sphere(self, sphere_id: int) -> list[Idea]:
        stmt = (
            select(*idea.c)
            .select_from(idea)
            .join(idea_sphere, idea.c.id == idea_sphere.c.idea_id)
            .where(idea_sphere.c.sphere_id == sphere_id)
        )

        with self._engine.connect() as conn:
            res: Result = conn.execute(stmt)
            rows = res.mappings().all()
            return [self._to_idea(row) for row in rows]

    def get_all_ideas(self) -> list[Idea]:
        with self._engine.connect() as conn:
            res: Result = conn.execute(select(*idea.c))
            rows = res.mappings().all()
            return [self._to_idea(row) for row in rows]

    def get_all_spheres(self) -> list[Sphere]:
        with self._engine.connect() as conn:
            res: Result = conn.execute(select(*sphere.c))
            rows = res.mappings().all()
            return [self._to_sphere(row) for row in rows]
