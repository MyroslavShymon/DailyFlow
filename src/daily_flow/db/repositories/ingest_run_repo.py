import logging
from collections.abc import Mapping
from dataclasses import asdict, dataclass
from datetime import datetime
from typing import Any

from sqlalchemy import exists, insert, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncEngine

from daily_flow.db.errors import MissingRequiredFieldError, UnknownFieldError, map_integrity_error
from daily_flow.db.schema.audit import IngestSourceType, IngestStatusType, ingest_run

logger = logging.getLogger(__name__)

ALLOWED_INGEST_FIELDS = {
    "dataset",
    "source_type",
    "source_path",
    "file_hash",
    "started_at",
    "finished_at",
    "status",
    "metrics",
    "error_message",
    "id",
}
REQUIRED_INGEST_FIELDS = {
    "dataset",
    "source_type",
    "source_path",
    "file_hash",
    "started_at",
    "finished_at",
    "status",
}


@dataclass(frozen=True)
class IngestRun:
    dataset: str
    source_type: IngestSourceType
    source_path: str
    file_hash: str
    started_at: datetime
    finished_at: datetime
    status: IngestStatusType
    metrics: dict[str, Any] | None = None
    error_message: str | None = None
    id: int | None = None


class IngestRunRepo:
    def __init__(self, engine: AsyncEngine) -> None:
        self._engine = engine

    @staticmethod
    def _to_ingest_run(row_mapping: Mapping[str, Any]) -> IngestRun:
        return IngestRun(
            id=row_mapping["id"],
            dataset=row_mapping["dataset"],
            source_type=row_mapping["source_type"],
            source_path=row_mapping["source_path"],
            file_hash=row_mapping["file_hash"],
            started_at=row_mapping["started_at"],
            finished_at=row_mapping["finished_at"],
            status=row_mapping["status"],
            metrics=row_mapping["metrics"],
            error_message=row_mapping["error_message"],
        )

    async def add_ingest(self, run: IngestRun) -> IngestRun:
        data = asdict(run)

        data.pop("id")

        run_fields = set(data)
        unknown_keys = run_fields - ALLOWED_INGEST_FIELDS
        if unknown_keys:
            raise UnknownFieldError(f"Unknown fields: {','.join(unknown_keys)}")

        missing_fields = REQUIRED_INGEST_FIELDS - run_fields
        if missing_fields:
            raise MissingRequiredFieldError(f"Missing required fields: {','.join(missing_fields)}")

        none_fields = {k for k in REQUIRED_INGEST_FIELDS if data.get(k) is None}
        if none_fields:
            raise MissingRequiredFieldError(
                f"Some of required fields are none: {','.join(none_fields)}"
            )

        try:
            async with self._engine.begin() as conn:
                res = await conn.execute(insert(ingest_run).values(**data).returning(*ingest_run.c))
                row = res.mappings().one()
                return self._to_ingest_run(row)
        except IntegrityError as e:
            logger.exception(
                "IngestRunRepo.add_ingest failed (source_path=%s, file_hash=%s)",
                run.source_path,
                run.file_hash,
            )
            raise map_integrity_error(e, ingest_run.name) from e

    async def is_already_processed(self, file_hash: str) -> bool:
        try:
            async with self._engine.connect() as conn:
                return bool(
                    await conn.scalar(select(exists().where(ingest_run.c.file_hash == file_hash)))
                )
        except IntegrityError as e:
            logger.exception(
                "IngestRunRepo.is_already_processed failed (file_hash=%s)",
                file_hash,
            )
            raise map_integrity_error(e, ingest_run.name) from e
