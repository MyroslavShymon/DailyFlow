import logging
from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Any, Mapping

from sqlalchemy.engine import Engine, Result
from sqlalchemy.exc import IntegrityError
from sqlalchemy.dialects.sqlite import insert as sqlite_insert
from sqlalchemy import select, delete, exists, and_

from daily_flow.db.errors import (
    map_integrity_error,
    MissingRequiredFieldError,
    UnknownFieldError,
    InvalidScoreError,
    ParentNotFoundError,
)
from daily_flow.db.schema import activity_usage, activity

logger = logging.getLogger(__name__)

ALLOWED_ACTIVITY_USAGE_FIELDS = {
    "duration_actual_minutes",
    "rating_before",
    "rating_after",
    "mood_before",
    "mood_after",
    "energy_before",
    "energy_after",
    "notes",
}


@dataclass(frozen=True)
class ActivityUsage:
    id: int
    activity_id: int
    used_at: datetime

    duration_actual_minutes: Optional[int]

    rating_before: Optional[int]
    rating_after: Optional[int]
    mood_before: Optional[int]
    mood_after: Optional[int]
    energy_before: Optional[int]
    energy_after: Optional[int]

    notes: Optional[str]


class ActivityUsageRepo:
    def __init__(self, engine: Engine) -> None:
        self._engine = engine

    @staticmethod
    def _to_activity_usage(row_mapping: Mapping[str, Any]) -> ActivityUsage:
        return ActivityUsage(
            id=row_mapping["id"],
            activity_id=row_mapping["activity_id"],
            used_at=row_mapping["used_at"],
            duration_actual_minutes=row_mapping["duration_actual_minutes"],
            rating_before=row_mapping["rating_before"],
            rating_after=row_mapping["rating_after"],
            mood_before=row_mapping["mood_before"],
            mood_after=row_mapping["mood_after"],
            energy_before=row_mapping["energy_before"],
            energy_after=row_mapping["energy_after"],
            notes=row_mapping["notes"],
        )

    @staticmethod
    def _usage_payload_validator(payload: dict[str, Any]) -> None:
        payload = payload or {}
        unknown_keys = set(payload) - ALLOWED_ACTIVITY_USAGE_FIELDS
        if unknown_keys:
            raise UnknownFieldError(f"Unknown fields: {','.join(sorted(unknown_keys))}")

    @staticmethod
    def _validate_scale_1_5(value: Any, field_name: str) -> None:
        if value is None:
            return
        if not isinstance(value, int) or not (1 <= value <= 5):
            raise InvalidScoreError(f"{field_name} must be int between 1 and 5")

    @staticmethod
    def _validate_non_negative_int(value: Any, field_name: str) -> None:
        if value is None:
            return
        if not isinstance(value, int) or value < 0:
            raise InvalidScoreError(f"{field_name} must be int >= 0")

    @staticmethod
    def _validate_before_after(payload: dict[str, Any]) -> None:
        if payload.get("rating_after") is not None and payload.get("rating_before") is None:
            raise MissingRequiredFieldError("rating_before is required when rating_after provided")
        if payload.get("mood_after") is not None and payload.get("mood_before") is None:
            raise MissingRequiredFieldError("mood_before is required when mood_after provided")
        if payload.get("energy_after") is not None and payload.get("energy_before") is None:
            raise MissingRequiredFieldError("energy_before is required when energy_after provided")

    @staticmethod
    def _assert_activity_exists(conn, activity_id: int) -> None:
        ok = conn.execute(
            select(exists().where(activity.c.id == activity_id))
        ).scalar()
        if not ok:
            raise ParentNotFoundError("There is no activity entity with such id")

    def upsert_activity_usage(
        self,
        activity_id: int,
        used_at: datetime,
        payload: dict[str, Any],
        usage_id: int | None = None,
    ) -> ActivityUsage:
        if not activity_id:
            raise MissingRequiredFieldError("activity_id is required")
        if not used_at:
            raise MissingRequiredFieldError("used_at is required")

        payload = payload or {}
        self._usage_payload_validator(payload)

        self._validate_non_negative_int(payload.get("duration_actual_minutes"), "duration_actual_minutes")

        self._validate_scale_1_5(payload.get("rating_before"), "rating_before")
        self._validate_scale_1_5(payload.get("rating_after"), "rating_after")
        self._validate_scale_1_5(payload.get("mood_before"), "mood_before")
        self._validate_scale_1_5(payload.get("mood_after"), "mood_after")
        self._validate_scale_1_5(payload.get("energy_before"), "energy_before")
        self._validate_scale_1_5(payload.get("energy_after"), "energy_after")

        self._validate_before_after(payload)

        try:
            with self._engine.begin() as conn:
                self._assert_activity_exists(conn, activity_id)

                base_values = {"activity_id": activity_id, "used_at": used_at}
                insert_values = {**base_values, **payload}

                if usage_id is None:
                    stmt = (
                        sqlite_insert(activity_usage)
                        .values(**insert_values)
                        .returning(*activity_usage.c)
                    )
                    res: Result = conn.execute(stmt)
                    row = res.mappings().one()
                    return self._to_activity_usage(row)

                insert_stmt = sqlite_insert(activity_usage).values(id=usage_id, **insert_values)

                set_fields = dict(base_values)
                set_fields.update({k: v for k, v in payload.items() if v is not None})

                stmt = (
                    insert_stmt
                    .on_conflict_do_update(
                        index_elements=[activity_usage.c.id],
                        set_=set_fields,
                    )
                    .returning(*activity_usage.c)
                )

                res2: Result = conn.execute(stmt)
                row2 = res2.mappings().one()
                return self._to_activity_usage(row2)

        except IntegrityError as e:
            logger.exception(
                "ActivityUsageRepo.upsert_activity_usage failed "
                "(usage_id=%s, activity_id=%s, used_at=%s, fields=%s)",
                usage_id,
                activity_id,
                str(used_at),
                list(payload.keys()),
            )
            raise map_integrity_error(e, activity_usage.name) from e

    def delete_activity_usage_by_id(self, usage_id: int) -> int:
        if not usage_id:
            raise MissingRequiredFieldError("usage_id is required")

        stmt = delete(activity_usage).where(activity_usage.c.id == usage_id)

        with self._engine.begin() as conn:
            res: Result = conn.execute(stmt)
            return int(res.rowcount or 0)

    def delete_activity_usages_by_activity(self, activity_id: int) -> int:
        if not activity_id:
            raise MissingRequiredFieldError("activity_id is required")

        stmt = delete(activity_usage).where(activity_usage.c.activity_id == activity_id)

        with self._engine.begin() as conn:
            res: Result = conn.execute(stmt)
            return int(res.rowcount or 0)

    def get_activity_usage_by_id(self, usage_id: int) -> ActivityUsage | None:
        stmt = select(*activity_usage.c).where(activity_usage.c.id == usage_id).limit(1)

        with self._engine.connect() as conn:
            res: Result = conn.execute(stmt)
            row = res.mappings().one_or_none()
            return self._to_activity_usage(row) if row else None

    def get_activity_usages_by_activity(self, activity_id: int) -> list[ActivityUsage]:
        stmt = (
            select(*activity_usage.c)
            .where(activity_usage.c.activity_id == activity_id)
            .order_by(activity_usage.c.used_at.desc())
        )

        with self._engine.connect() as conn:
            res: Result = conn.execute(stmt)
            rows = res.mappings().all()
            return [self._to_activity_usage(row) for row in rows]

    def get_activity_usages_by_period(self, date_from: datetime, date_to: datetime) -> list[ActivityUsage]:
        if not date_from or not date_to:
            raise MissingRequiredFieldError("date_from and date_to are required")

        stmt = (
            select(*activity_usage.c)
            .where(
                and_(
                    activity_usage.c.used_at >= date_from,
                    activity_usage.c.used_at <= date_to,
                )
            )
            .order_by(activity_usage.c.used_at.desc())
        )

        with self._engine.connect() as conn:
            res: Result = conn.execute(stmt)
            rows = res.mappings().all()
            return [self._to_activity_usage(row) for row in rows]

    def get_last_activity_usages(self, limit: int) -> list[ActivityUsage]:
        if not limit or limit <= 0:
            raise MissingRequiredFieldError("limit must be > 0")

        stmt = select(*activity_usage.c).order_by(activity_usage.c.used_at.desc()).limit(limit)

        with self._engine.connect() as conn:
            res: Result = conn.execute(stmt)
            rows = res.mappings().all()
            return [self._to_activity_usage(row) for row in rows]
