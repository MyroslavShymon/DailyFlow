import logging
from dataclasses import dataclass
from datetime import date, datetime
from typing import Optional, Any, Mapping, TypedDict

from sqlalchemy.engine import Engine, Result
from sqlalchemy import select, delete, and_, func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.dialects.sqlite import insert as sqlite_insert

from daily_flow.db.errors import EmptyUpsertPayloadError, UnknownFieldError, MissingRequiredFieldError, \
    map_integrity_error, InvalidScoreError, ParentNotFoundError
from daily_flow.db.repositories.mood_log_repo import NON_UPDATABLE
from daily_flow.db.schema import common_mood_log, mood_tag_impact

ALLOWED_COMMON_MOOD_FIELDS = {"mood", "note"}
COMMON_MOOD_NON_UPDATABLE = {'day', 'id', 'created_at'}
ALLOWED_MOOD_TAG_FIELDS = {"tag", "impact"}

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class CommonMoodLog:
    id: int
    day: date
    mood: int
    note: Optional[str]
    created_at: datetime


@dataclass(frozen=True)
class MoodTagImpact:
    id: int
    common_mood_log_id: int
    tag: str
    impact: int


class CommonMoodLogValues(TypedDict):
    mood: Optional[int | None]
    note: Optional[str | None]


class DayPayload(TypedDict):
    day: date
    values: CommonMoodLogValues


@dataclass(frozen=True)
class BatchCommonMoodLogUpsertResult:
    rows_in: int
    rows_written: int
    min_day: date | None
    max_day: date | None


class CommonMoodLogRepo:
    def __init__(self, engine: Engine) -> None:
        self._engine = engine

    @staticmethod
    def _to_common_mood_log(row_mapping: Mapping[str, Any]) -> CommonMoodLog:
        return CommonMoodLog(
            id=row_mapping["id"],
            day=row_mapping["day"],
            mood=row_mapping["mood"],
            note=row_mapping["note"],
            created_at=row_mapping["created_at"],
        )

    @staticmethod
    def _to_mood_tag_impact(row_mapping: Mapping[str, Any]) -> MoodTagImpact:
        return MoodTagImpact(
            id=row_mapping["id"],
            common_mood_log_id=row_mapping["common_mood_log_id"],
            tag=row_mapping["tag"],
            impact=row_mapping["impact"],
        )

    @staticmethod
    def _common_mood_log_payload_validator(
            payload: dict[str, Any]
    ) -> None:
        if not payload or all(p is None for p in payload.values()):
            raise EmptyUpsertPayloadError("No fields to upsert")
        unknown_keys = set(payload) - ALLOWED_COMMON_MOOD_FIELDS
        if unknown_keys:
            raise UnknownFieldError(f"Unknown fields: {','.join(unknown_keys)}")

    def upsert_common_mood_log_by_day(
            self,
            day: date,
            payload: dict[str, Any]
    ) -> CommonMoodLog:
        self._common_mood_log_payload_validator(payload=payload)

        try:
            with self._engine.begin() as conn:
                if "mood" in payload and payload["mood"] is not None:
                    mood = payload["mood"]
                    if not isinstance(mood, int) or not (1 <= mood <= 7):
                        raise InvalidScoreError("mood must be int between 1 and 7")

                exists = conn.execute(
                    select(common_mood_log.c.id)
                    .where(common_mood_log.c.day == day)
                ).first()

                if not exists and payload.get("mood") is None:
                    raise MissingRequiredFieldError("mood is required for the first insert")

                stmt = (
                    sqlite_insert(common_mood_log)
                    .values(day=day, **payload)
                    .on_conflict_do_update(
                        index_elements=[common_mood_log.c.day],
                        set_={k: p for k, p in payload.items() if p is not None}
                    )
                    .returning(*common_mood_log.c)
                )

                res: Result = conn.execute(stmt)
                row = res.mappings().one()
                return self._to_common_mood_log(row)
        except IntegrityError as e:
            logger.exception(
                "CommonMoodLogRepo.upsert_common_mood_log_by_day failed "
                "(day=%s, fields=%s)",
                day,
                list(payload.keys()),
            )
            raise map_integrity_error(e, common_mood_log.name) from e

    def batch_upsert_common_mood_logs(self, payload: list[DayPayload]) -> BatchCommonMoodLogUpsertResult:
        if not payload:
            return BatchCommonMoodLogUpsertResult(rows_in=0, rows_written=0, min_day=None, max_day=None)

        flattened_data = []
        for p in payload:
            if not p.get("day"):
                raise EmptyUpsertPayloadError("There is no day value to upsert common mood log")
            self._common_mood_log_payload_validator(payload=p.get("values"))
            flattened_data.append({"day": p["day"], **p["values"]})

        rows_in = len(payload)
        min_day = min(p['day'] for p in payload)
        max_day = max(p['day'] for p in payload)

        stmt = sqlite_insert(common_mood_log).values(flattened_data)

        upsert_stmt = stmt.on_conflict_do_update(
            index_elements=[common_mood_log.c.day],
            set_={
                table_col.name:
                    func.coalesce(
                        stmt.excluded[table_col.name],
                        common_mood_log.c[table_col.name]
                    )
                for table_col in common_mood_log.c
                if table_col.name not in NON_UPDATABLE
            }
        )

        try:
            with self._engine.begin() as conn:
                res: Result = conn.execute(upsert_stmt)
                rows_written = int(res.rowcount or 0)

                return BatchCommonMoodLogUpsertResult(
                    rows_in=rows_in,
                    rows_written=rows_written,
                    min_day=min_day,
                    max_day=max_day
                )
        except IntegrityError as e:
            logger.exception(
                "CommonMoodLogRepo.batch_upsert_common_mood_logs failed "
                "(min_day=%s, max_day=%s)",
                str(min_day),
                str(max_day),
            )
            raise map_integrity_error(e, common_mood_log.name) from e


    def get_common_mood_log_by_day(self, day: date) -> CommonMoodLog | None:
        stmt = (
            select(*common_mood_log.c)
            .where(common_mood_log.c.day == day)
            .limit(1)
        )

        with self._engine.connect() as conn:
            res: Result = conn.execute(stmt)
            row = res.mappings().one_or_none()
            return self._to_common_mood_log(row) if row else None


    def upsert_tag_by_day(
            self,
            day: date,
            payload: dict[str, Any]
    ) -> MoodTagImpact:
        if not payload or all(p is None for p in payload.values()):
            raise EmptyUpsertPayloadError("No fields to upsert")

        unknown_keys = set(payload) - ALLOWED_MOOD_TAG_FIELDS
        if unknown_keys:
            raise UnknownFieldError(f"Unknown fields: {','.join(unknown_keys)}")

        try:
            with self._engine.begin() as conn:
                common_mood_id: int | None = conn.execute(
                    select(common_mood_log.c.id)
                    .where(common_mood_log.c.day == day)
                ).scalar()

                if not common_mood_id:
                    raise ParentNotFoundError(f"There is no common mood log in this day: {day}")
                tag = payload.get("tag")
                impact = payload.get("impact")

                if not tag:
                    raise MissingRequiredFieldError("tag is required")
                tag = tag.strip().lower()
                if not tag:
                    raise MissingRequiredFieldError("tag is required")

                if impact is None:
                    raise MissingRequiredFieldError("impact is required")
                if not isinstance(impact, int) or impact not in (-1, 0, 1):
                    raise InvalidScoreError("impact must be one of -1, 0, 1")

                insert_data = {
                    "common_mood_log_id": common_mood_id,
                    "tag": tag,
                    "impact": impact,
                }

                stmt = (
                    sqlite_insert(mood_tag_impact)
                    .values(**insert_data)
                    .on_conflict_do_update(
                        index_elements=[mood_tag_impact.c.common_mood_log_id, mood_tag_impact.c.tag],
                        set_={"impact": impact}
                    )
                    .returning(*mood_tag_impact.c)
                )

                res: Result = conn.execute(stmt)
                raw = res.mappings().one()
                return self._to_mood_tag_impact(raw)
        except IntegrityError as e:
            logger.exception(
                "CommonMoodLogRepo.upsert_tag_for_day failed "
                "(day=%s, fields=%s)",
                day,
                list(payload.keys()),
            )
            raise map_integrity_error(e, mood_tag_impact.name) from e


    def get_tags_by_day(self, day: date) -> list[MoodTagImpact]:
        with self._engine.connect() as conn:
            common_mood_id: int | None = conn.execute(
                select(common_mood_log.c.id)
                .where(common_mood_log.c.day == day)
            ).scalar()

            if not common_mood_id:
                return []

            stmt = (
                select(*mood_tag_impact.c)
                .where(mood_tag_impact.c.common_mood_log_id == common_mood_id)
                .order_by(mood_tag_impact.c.tag)
            )

            res: Result = conn.execute(stmt)
            rows = res.mappings().all()
            return [self._to_mood_tag_impact(row) for row in rows]


    def delete_tag_by_day(self, day: date, tag: str) -> int:
        tag = tag.strip().lower()
        if not tag:
            raise MissingRequiredFieldError("tag is required")

        with self._engine.begin() as conn:
            common_mood_id: int | None = conn.execute(
                select(common_mood_log.c.id)
                .where(common_mood_log.c.day == day)
            ).scalar()

            if not common_mood_id:
                raise ParentNotFoundError(f"There is no common mood log in this day: {day}")

            stmt = (
                delete(mood_tag_impact)
                .where(
                    and_(
                        mood_tag_impact.c.common_mood_log_id == common_mood_id,
                        mood_tag_impact.c.tag == tag
                    )
                )
            )

            res: Result = conn.execute(stmt)
            return int(res.rowcount or 0)


    def get_all_unique_tags(self) -> list[str]:
        with self._engine.connect() as conn:
            stmt = (
                select(mood_tag_impact.c.tag)
                .distinct()
                .order_by(mood_tag_impact.c.tag)
            )

            res = conn.execute(stmt)
            rows = res.scalars().all()
            return [str(row) for row in rows]
