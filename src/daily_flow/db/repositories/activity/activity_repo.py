import logging
from dataclasses import dataclass
from typing import Optional, Any, Mapping

from sqlalchemy.engine import Engine, Result
from sqlalchemy.exc import IntegrityError
from sqlalchemy.dialects.sqlite import insert as sqlite_insert
from sqlalchemy import select, delete, update, and_

from daily_flow.db.errors import map_integrity_error, MissingRequiredFieldError, UnknownFieldError
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
    description: Optional[str]

    social_type: Optional[str]
    people_count_min: Optional[int]
    people_count_max: Optional[int]
    specific_with: Optional[str]

    time_context: Optional[str]
    duration_min_minutes: Optional[int]
    duration_max_minutes: Optional[int]
    time_of_day: Optional[str]

    energy_required_min: Optional[int]
    energy_required_max: Optional[int]
    energy_gain: Optional[int]
    mood_min: Optional[int]
    mood_max: Optional[int]

    cost_level: Optional[str]
    requires_preparation: bool
    preparation_notes: Optional[str]
    location_type: Optional[str]


class ActivityRepo:
    def __init__(self, engine: Engine) -> None:
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

    def upsert_activity(self, title: str, payload: dict[str, Any]) -> Activity:
        title = (title or "").strip()
        if not title:
            raise MissingRequiredFieldError("Invalid format error for title field")

        payload = payload or {}
        self._activity_payload_validator(payload)

        fields_to_update = {k: v for k, v in payload.items() if v is not None}

        try:
            with self._engine.begin() as conn:
                activity_id: int | None = conn.execute(
                    select(activity.c.id)
                    .where(activity.c.title == title)
                    .limit(1)
                ).scalar()

                if activity_id is None:
                    stmt = (
                        sqlite_insert(activity)
                        .values(title=title, **payload)
                        .returning(*activity.c)
                    )
                    res: Result = conn.execute(stmt)
                    row = res.mappings().one()
                    return self._to_activity(row)

                if fields_to_update:
                    stmt = (
                        update(activity)
                        .where(activity.c.id == activity_id)
                        .values(**fields_to_update)
                        .returning(*activity.c)
                    )
                    res: Result = conn.execute(stmt)
                    row = res.mappings().one()
                    return self._to_activity(row)

                row = conn.execute(
                    select(*activity.c).where(activity.c.id == activity_id)
                ).mappings().one()
                return self._to_activity(row)

        except IntegrityError as e:
            logger.exception(
                "ActivityRepo.upsert_activity failed (title=%s, fields=%s)",
                title,
                list(payload.keys()),
            )
            raise map_integrity_error(e, activity.name) from e

    def delete_activity_by_title(self, title: str) -> int:
        title = (title or "").strip()
        if not title:
            raise MissingRequiredFieldError("title is required")

        stmt = delete(activity).where(activity.c.title == title)

        with self._engine.begin() as conn:
            res: Result = conn.execute(stmt)
            return int(res.rowcount or 0)

    def delete_activity_by_id(self, activity_id: int) -> int:
        if not activity_id:
            raise MissingRequiredFieldError("activity_id is required")

        stmt = delete(activity).where(activity.c.id == activity_id)

        with self._engine.begin() as conn:
            res: Result = conn.execute(stmt)
            return int(res.rowcount or 0)

    def get_activity_by_id(self, activity_id: int) -> Activity | None:
        stmt = select(*activity.c).where(activity.c.id == activity_id).limit(1)

        with self._engine.connect() as conn:
            res: Result = conn.execute(stmt)
            row = res.mappings().one_or_none()
            return self._to_activity(row) if row else None

    def get_activity_by_title(self, title: str) -> Activity | None:
        title = (title or "").strip()
        if not title:
            raise MissingRequiredFieldError("title is required")

        stmt = select(*activity.c).where(activity.c.title == title).limit(1)

        with self._engine.connect() as conn:
            res: Result = conn.execute(stmt)
            row = res.mappings().one_or_none()
            return self._to_activity(row) if row else None

    def get_all_activities(self) -> list[Activity]:
        stmt = select(*activity.c).order_by(activity.c.title)

        with self._engine.connect() as conn:
            res: Result = conn.execute(stmt)
            rows = res.mappings().all()
            return [self._to_activity(row) for row in rows]

    def get_activities_by_category(self, category_id: int) -> list[Activity]:
        stmt = (
            select(*activity.c)
            .select_from(activity)
            .join(category_activity, activity.c.id == category_activity.c.activity_id)
            .where(category_id == category_activity.c.category_id)
            .order_by(activity.c.title)
        )

        with self._engine.connect() as conn:
            res: Result = conn.execute(stmt)
            rows = res.mappings().all()
            return [self._to_activity(row) for row in rows]
