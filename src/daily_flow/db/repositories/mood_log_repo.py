import logging
from dataclasses import dataclass
from datetime import datetime, date
from typing import Optional, Any, Mapping, TypedDict

from sqlalchemy.engine import Engine, Result
from sqlalchemy import select, delete, func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.dialects.sqlite import insert as sqlite_insert

from daily_flow.db.errors import map_integrity_error, EmptyUpsertPayloadError, UnknownFieldError
from daily_flow.db.schema import mood_log

ALLOWED_SCORE_FIELDS =  {"joy", "interest", "calm", "energy", "anxiety", "sadness", "irritation", "fatigue", "fear",
                     "confidence", "sleep"}

NON_UPDATABLE = {'day', 'id', 'created_at'}

logger = logging.getLogger(__name__)

@dataclass(frozen=True)
class MoodLog:
    id: int
    day: date
    joy: Optional[int]
    interest: Optional[int]
    calm: Optional[int]
    energy: Optional[int]
    anxiety: Optional[int]
    sadness: Optional[int]
    irritation: Optional[int]
    fatigue: Optional[int]
    fear: Optional[int]
    confidence: Optional[int]
    sleep: Optional[int]
    created_at: datetime

class MoodValues(TypedDict):
    joy: Optional[int | None]
    interest: Optional[int | None]
    calm: Optional[int | None]
    energy: Optional[int | None]
    anxiety: Optional[int | None]
    sadness: Optional[int | None]
    irritation: Optional[int | None]
    fatigue: Optional[int | None]
    fear: Optional[int | None]
    confidence: Optional[int | None]
    sleep: Optional[int | None]

class DayPayload(TypedDict):
    day: date
    values: MoodValues

@dataclass(frozen=True)
class BatchMoodLogUpsertResult:
    rows_in: int
    rows_written: int
    min_day: date | None
    max_day: date | None

class MoodLogRepo:
    def __init__(self, engine: Engine) -> None:
        self._engine = engine

    @staticmethod
    def _to_mood_log(row_mapping: Mapping[str, Any]) -> MoodLog:
        return MoodLog(
            id=row_mapping["id"],
            day=row_mapping["day"],
            joy=row_mapping["joy"],
            interest=row_mapping["interest"],
            calm=row_mapping["calm"],
            energy=row_mapping["energy"],
            anxiety=row_mapping["anxiety"],
            sadness=row_mapping["sadness"],
            irritation=row_mapping["irritation"],
            fatigue=row_mapping["fatigue"],
            fear=row_mapping["fear"],
            confidence=row_mapping["confidence"],
            sleep=row_mapping["sleep"],
            created_at=row_mapping["created_at"],
        )

    @staticmethod
    def _mood_values_validator(
            values: dict[str, int | None],
    ) -> None:
        if not values or all(v is None for v in values.values()):
            raise EmptyUpsertPayloadError("No fields to upsert")
        unknown_keys = set(values) - ALLOWED_SCORE_FIELDS
        if unknown_keys:
            raise UnknownFieldError(f"Unknown fields: {','.join(unknown_keys)}")

    def upsert_mood_log_by_day(
            self,
            day: date,
            values: dict[str, int | None],
    ) -> MoodLog:
        self._mood_values_validator(values=values)

        stmt = (
            sqlite_insert(mood_log)
            .values(day=day, **values)
            .on_conflict_do_update(
                index_elements=[mood_log.c.day],
                set_={k: v for k, v in values.items() if v is not None}
            )
            .returning(*mood_log.c)
        )

        try:
            with self._engine.begin() as conn:
                res: Result = conn.execute(stmt)
                row = res.mappings().one()
                return self._to_mood_log(row)
        except IntegrityError as e:
            logger.exception(
                "MoodLogRepo.upsert_mood_log_by_day failed "
                "(day=%s, fields=%s)",
                day,
                list(values.keys()),
            )
            raise map_integrity_error(e, mood_log.name) from e

    def batch_upsert_mood_logs(self, payload: list[DayPayload]) -> BatchMoodLogUpsertResult:
        if not payload:
            return BatchMoodLogUpsertResult(rows_in=0, rows_written=0, min_day=None, max_day=None)

        flattened_data = []
        for p in payload:
            if not p.get("day"):
                raise EmptyUpsertPayloadError("There is no day value to upsert")
            self._mood_values_validator(values=p["values"])
            flattened_data.append({"day": p["day"], **p["values"]})

        rows_in = len(payload)
        min_day = min(p['day'] for p in payload)
        max_day = max(p['day'] for p in payload)

        stmt = sqlite_insert(mood_log).values(flattened_data)

        upsert_stmt = stmt.on_conflict_do_update(
                index_elements=[mood_log.c.day],
                set_ = {
                    table_col.name:
                        func.coalesce(
                            stmt.excluded[table_col.name],
                            mood_log.c[table_col.name]
                        )
                    for table_col in mood_log.c
                    if table_col.name not in NON_UPDATABLE
                }
        )

        try:
            with self._engine.begin() as conn:
                res: Result = conn.execute(upsert_stmt)
                rows_written = int(res.rowcount or 0)

                return BatchMoodLogUpsertResult(
                    rows_in=rows_in,
                    rows_written=rows_written,
                    min_day=min_day,
                    max_day=max_day
                )
        except IntegrityError as e:
            logger.exception(
                "MoodLogRepo.batch_upsert_mood_logs failed "
                "(min_day=%s, max_day=%s)",
                str(min_day),
                str(max_day),
            )
            raise map_integrity_error(e, mood_log.name) from e

    def get_mood_log_by_day(self, day: date) -> MoodLog | None:
        stmt = (
            select(*mood_log.c)
            .where(mood_log.c.day == day)
            .limit(1)
        )

        with self._engine.connect() as conn:
            res: Result = conn.execute(stmt)
            row = res.mappings().one_or_none()
            return self._to_mood_log(row) if row else None

    def list_by_date_range(self, start: date, end: date) -> list[MoodLog]:
        stmt = (
            select(*mood_log.c)
            .where(mood_log.c.day.between(start, end))
            .order_by(mood_log.c.day.asc())
        )

        with self._engine.connect() as conn:
            res: Result = conn.execute(stmt)
            rows = res.mappings().all()
            return [self._to_mood_log(row) for row in rows]

    def delete_mood_log_by_day(self, day: date) -> int:
        stmt = (
            delete(mood_log)
            .where(mood_log.c.day == day)
        )

        with self._engine.begin() as conn:
            res: Result = conn.execute(stmt)
            return int(res.rowcount or 0)
