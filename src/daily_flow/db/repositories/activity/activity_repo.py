import logging
from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any

from sqlalchemy import CursorResult, delete, select, update
from sqlalchemy.dialects.sqlite import insert as sqlite_insert
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncEngine

from daily_flow.db.errors import MissingRequiredFieldError, UnknownFieldError, map_integrity_error
from daily_flow.db.schema import activity, category_activity

logger = logging.getLogger(__name__)

ALLOWED_ACTIVITY_FIELDS = {
    "description",
    "social_type",
    "people_count_min",
    "people_count_max",
    "specific_with",
    "time_context",
    "duration_min_minutes",
    "duration_max_minutes",
    "time_of_day",
    "energy_required_min",
    "energy_required_max",
    "energy_gain",
    "mood_min",
    "mood_max",
    "cost_level",
    "requires_preparation",
    "preparation_notes",
    "location_type",
}


@dataclass(frozen=True)
class Activity:
    id: int
    title: str
    description: str | None

    social_type: str | None
    people_count_min: int | None
    people_count_max: int | None
    specific_with: str | None

    time_context: str | None
    duration_min_minutes: int | None
    duration_max_minutes: int | None
    time_of_day: str | None

    energy_required_min: int | None
    energy_required_max: int | None
    energy_gain: int | None
    mood_min: int | None
    mood_max: int | None

    cost_level: str | None
    requires_preparation: bool
    preparation_notes: str | None
    location_type: str | None


class ActivityRepo:
    def __init__(self, engine: AsyncEngine) -> None:
        self._engine = engine

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
    def _activity_payload_validator(payload: dict[str, Any]) -> None:
        unknown_keys = set(payload) - ALLOWED_ACTIVITY_FIELDS
        if unknown_keys:
            raise UnknownFieldError(f"Unknown fields: {','.join(sorted(unknown_keys))}")

    async def upsert_activity(self, title: str, payload: dict[str, Any]) -> Activity:
        title = (title or "").strip()
        if not title:
            raise MissingRequiredFieldError("Invalid format error for title field")

        payload = payload or {}
        self._activity_payload_validator(payload)

        fields_to_update = {k: v for k, v in payload.items() if v is not None}

        try:
            async with self._engine.begin() as conn:
                activity_id: int | None = (
                    await conn.execute(
                        select(activity.c.id).where(activity.c.title == title).limit(1)
                    )
                ).scalar()

                if activity_id is None:
                    stmt = (
                        sqlite_insert(activity)
                        .values(title=title, **payload)
                        .returning(*activity.c)
                    )
                    res = await conn.execute(stmt)
                    row = res.mappings().one()
                    return self._to_activity(row)

                if fields_to_update:
                    stmt = (
                        update(activity)
                        .where(activity.c.id == activity_id)
                        .values(**fields_to_update)
                        .returning(*activity.c)
                    )
                    res = await conn.execute(stmt)
                    row = res.mappings().one()
                    return self._to_activity(row)

                res = await conn.execute(
                    select(*activity.c).where(activity.c.id == activity_id).limit(1)
                )
                row = res.mappings().one()
                return self._to_activity(row)

        except IntegrityError as e:
            logger.exception(
                "ActivityRepo.upsert_activity failed (title=%s, fields=%s)",
                title,
                list(payload.keys()),
            )
            raise map_integrity_error(e, activity.name) from e

    async def delete_activity_by_title(self, title: str) -> int:
        title = (title or "").strip()
        if not title:
            raise MissingRequiredFieldError("title is required")

        stmt = delete(activity).where(activity.c.title == title)

        async with self._engine.begin() as conn:
            res: CursorResult = await conn.execute(stmt)
            return int(res.rowcount or 0)

    async def delete_activity_by_id(self, activity_id: int) -> int:
        if not activity_id:
            raise MissingRequiredFieldError("activity_id is required")

        stmt = delete(activity).where(activity.c.id == activity_id)

        async with self._engine.begin() as conn:
            res: CursorResult = await conn.execute(stmt)
            return int(res.rowcount or 0)

    async def get_activity_by_id(self, activity_id: int) -> Activity | None:
        stmt = select(*activity.c).where(activity.c.id == activity_id).limit(1)

        async with self._engine.connect() as conn:
            res = await conn.execute(stmt)
            row = res.mappings().one_or_none()
            return self._to_activity(row) if row else None

    async def get_activity_by_title(self, title: str) -> Activity | None:
        title = (title or "").strip()
        if not title:
            raise MissingRequiredFieldError("title is required")

        stmt = select(*activity.c).where(activity.c.title == title).limit(1)

        async with self._engine.connect() as conn:
            res = await conn.execute(stmt)
            row = res.mappings().one_or_none()
            return self._to_activity(row) if row else None

    async def get_all_activities(self) -> list[Activity]:
        stmt = select(*activity.c).order_by(activity.c.title)

        async with self._engine.connect() as conn:
            res = await conn.execute(stmt)
            rows = res.mappings().all()
            return [self._to_activity(row) for row in rows]

    async def get_activities_by_category(self, category_id: int) -> list[Activity]:
        stmt = (
            select(*activity.c)
            .select_from(activity)
            .join(category_activity, activity.c.id == category_activity.c.activity_id)
            .where(category_id == category_activity.c.category_id)
            .order_by(activity.c.title)
        )

        async with self._engine.connect() as conn:
            res = await conn.execute(stmt)
            rows = res.mappings().all()
            return [self._to_activity(row) for row in rows]
