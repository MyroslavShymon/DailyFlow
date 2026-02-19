import logging
from dataclasses import dataclass
from typing import Optional, Any, Mapping

from sqlalchemy.engine import Engine, Result
from sqlalchemy.exc import IntegrityError
from sqlalchemy.dialects.sqlite import insert as sqlite_insert
from sqlalchemy import select, delete

from daily_flow.db.errors import map_integrity_error, MissingRequiredFieldError
from daily_flow.db.schema import category

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class Category:
    id: int
    name: str
    description: Optional[str]


class CategoryRepo:
    def __init__(self, engine: Engine) -> None:
        self._engine = engine

    @staticmethod
    def _to_category(row_mapping: Mapping[str, Any]) -> Category:
        return Category(
            id=row_mapping["id"],
            name=row_mapping["name"],
            description=row_mapping["description"],
        )

    def upsert_category(self, name: str, description: str | None) -> Category:
        name = (name or "").strip()
        if not name:
            raise MissingRequiredFieldError("Name param is empty to upsert.")

        insert_stmt = sqlite_insert(category).values(name=name, description=description)

        if description is None:
            stmt = (
                insert_stmt
                .on_conflict_do_nothing(index_elements=[category.c.name])
                .returning(*category.c)
            )
        else:
            stmt = (
                insert_stmt
                .on_conflict_do_update(
                    index_elements=[category.c.name],
                    set_={"description": description},
                )
                .returning(*category.c)
            )

        try:
            with self._engine.begin() as conn:
                res: Result = conn.execute(stmt)
                row = res.mappings().one_or_none()
                if row is None:
                    row = conn.execute(
                        select(category).where(category.c.name == name)
                    ).mappings().one()
                return self._to_category(row)
        except IntegrityError as e:
            logger.exception(
                "CategoryRepo.upsert_category failed (name=%s, description=%s)",
                name,
                description,
            )
            raise map_integrity_error(e, category.name) from e

    def delete_category_by_name(self, name: str) -> int:
        name = (name or "").strip()
        if not name:
            raise MissingRequiredFieldError("name is required")

        stmt = delete(category).where(category.c.name == name)

        with self._engine.begin() as conn:
            res: Result = conn.execute(stmt)
            return int(res.rowcount or 0)

    def delete_category_by_id(self, category_id: int) -> int:
        if not category_id:
            raise MissingRequiredFieldError("category_id is required")

        stmt = delete(category).where(category.c.id == category_id)

        with self._engine.begin() as conn:
            res: Result = conn.execute(stmt)
            return int(res.rowcount or 0)

    def get_category_by_id(self, category_id: int) -> Category | None:
        stmt = select(*category.c).where(category.c.id == category_id).limit(1)

        with self._engine.connect() as conn:
            res: Result = conn.execute(stmt)
            row = res.mappings().one_or_none()
            return self._to_category(row) if row else None

    def get_category_by_name(self, name: str) -> Category | None:
        name = (name or "").strip()
        if not name:
            raise MissingRequiredFieldError("name is required")

        stmt = select(*category.c).where(category.c.name == name).limit(1)

        with self._engine.connect() as conn:
            res: Result = conn.execute(stmt)
            row = res.mappings().one_or_none()
            return self._to_category(row) if row else None

    def get_all_categories(self) -> list[Category]:
        stmt = select(*category.c).order_by(category.c.name)

        with self._engine.connect() as conn:
            res: Result = conn.execute(stmt)
            rows = res.mappings().all()
            return [self._to_category(row) for row in rows]
