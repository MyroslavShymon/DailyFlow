import logging
from typing import Mapping, Any

from sqlalchemy.ext.asyncio import AsyncEngine
from sqlalchemy.exc import IntegrityError
from sqlalchemy.dialects.sqlite import insert as sqlite_insert
from sqlalchemy import select, delete, exists, and_, CursorResult

from daily_flow.db.errors import map_integrity_error, ParentNotFoundError
from daily_flow.db.schema import activity, category, category_activity
from daily_flow.db.repositories.activity.activity_repo import Activity
from daily_flow.db.repositories.activity.category_repo import Category

logger = logging.getLogger(__name__)


class ActivityCategoryRepo:
    def __init__(self, engine: AsyncEngine) -> None:
        self._engine = engine

    @staticmethod
    def _to_category(row_mapping: Mapping[str, Any]) -> Category:
        return Category(
            id=row_mapping["id"],
            name=row_mapping["name"],
            description=row_mapping["description"],
        )

    @staticmethod
    def _to_activity(row_mapping: Mapping[str, Any]) -> Activity:
        return Activity(
            id=row_mapping["id"],
            title=row_mapping["title"],
            description=row_mapping["description"],

            social_type=row_mapping["social_type"],
            people_count_min=row_mapping["people_count_min"],
            people_count_max=row_mapping["people_count_max"],
            specific_with=row_mapping["specific_with"],

            time_context=row_mapping["time_context"],
            duration_min_minutes=row_mapping["duration_min_minutes"],
            duration_max_minutes=row_mapping["duration_max_minutes"],
            time_of_day=row_mapping["time_of_day"],

            energy_required_min=row_mapping["energy_required_min"],
            energy_required_max=row_mapping["energy_required_max"],
            energy_gain=row_mapping["energy_gain"],
            mood_min=row_mapping["mood_min"],
            mood_max=row_mapping["mood_max"],

            cost_level=row_mapping["cost_level"],
            requires_preparation=bool(row_mapping["requires_preparation"]),
            preparation_notes=row_mapping["preparation_notes"],
            location_type=row_mapping["location_type"],
        )

    @staticmethod
    async def _assert_exists(conn, table, entity_id: int, name: str) -> None:
        exists_row = (await conn.execute(
            select(exists().where(table.c.id == entity_id))
        )).scalar()

        if not exists_row:
            raise ParentNotFoundError(f"There is no {name} entity with such id")

    async def assign_category_to_activity(self, category_id: int, activity_id: int) -> bool:
        try:
            async with self._engine.begin() as conn:
                await self._assert_exists(conn, activity, activity_id, "activity")
                await self._assert_exists(conn, category, category_id, "category")

                stmt = (
                    sqlite_insert(category_activity)
                    .values(category_id=category_id, activity_id=activity_id)
                    .on_conflict_do_nothing(
                        index_elements=[category_activity.c.category_id, category_activity.c.activity_id]
                    )
                )


                res: CursorResult = await conn.execute(stmt)
                return (res.rowcount or 0) > 0

        except IntegrityError as e:
            logger.exception(
                "ActivityCategoryRepo.assign_category_to_activity failed "
                "(category_id=%s, activity_id=%s)",
                category_id,
                activity_id,
            )
            raise map_integrity_error(e, category_activity.name) from e

    async def delete_category_from_activity(self, category_id: int, activity_id: int) -> int:
        async with self._engine.begin() as conn:
            await self._assert_exists(conn, activity, activity_id, "activity")
            await self._assert_exists(conn, category, category_id, "category")

            stmt = (
                delete(category_activity)
                .where(
                    and_(
                        category_activity.c.category_id == category_id,
                        category_activity.c.activity_id == activity_id,
                    )
                )
            )

            res: CursorResult = await conn.execute(stmt)
            return int(res.rowcount or 0)

    async def get_categories_by_activity(self, activity_id: int) -> list[Category]:
        stmt = (
            select(*category.c)
            .select_from(category)
            .join(category_activity, category.c.id == category_activity.c.category_id)
            .where(category_activity.c.activity_id == activity_id)
            .order_by(category.c.name)
        )

        async with self._engine.connect() as conn:
            res = await conn.execute(stmt)
            rows = res.mappings().all()
            return [self._to_category(row) for row in rows]

    async def get_activities_by_category(self, category_id: int) -> list[Activity]:
        stmt = (
            select(*activity.c)
            .select_from(activity)
            .join(category_activity, activity.c.id == category_activity.c.activity_id)
            .where(category_activity.c.category_id == category_id)
            .order_by(activity.c.title)
        )

        async with self._engine.connect() as conn:
            res = await conn.execute(stmt)
            rows = res.mappings().all()
            return [self._to_activity(row) for row in rows]
