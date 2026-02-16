import logging
from dataclasses import dataclass, asdict
from datetime import datetime
from typing import Optional, Any, Mapping

from sqlalchemy.engine import Engine, Result
from sqlalchemy import insert, select
from sqlalchemy.exc import IntegrityError

from daily_flow.db.errors import map_integrity_error, UnknownFieldError, MissingRequiredFieldError
from daily_flow.db.schema.audit import ingest_run, IngestSourceType, IngestStatusType

logger = logging.getLogger(__name__)

ALLOWED_INGEST_FIELDS = {"dataset", "source_type", "source_path", "file_hash", "started_at", "finished_at", "status", "metrics", "error_message", "id"}
REQUIRED_INGEST_FIELDS = {"dataset", "source_type", "source_path", "file_hash", "started_at", "finished_at", "status"}


@dataclass(frozen=True)
class IngestRun:
    dataset: str
    source_type: IngestSourceType
    source_path: str
    file_hash: str
    started_at: datetime
    finished_at: datetime
    status: IngestStatusType
    metrics: Optional[dict[str, Any]] = None
    error_message: Optional[str] = None
    id: Optional[int] = None

class IngestRunRepo:
    def __init__(self, engine: Engine) -> None:
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

    def add_ingest(self, run: IngestRun) -> IngestRun:
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
            raise MissingRequiredFieldError(f"Some of required fields are none: {','.join(none_fields)}")

        try:
            with self._engine.begin() as conn:
                res: Result = conn.execute(
                    insert(ingest_run)
                    .values(**data)
                    .returning(*ingest_run.c)
                )
                row = res.mappings().one()
                return self._to_ingest_run(row)
        except IntegrityError as e:
            logger.exception(
                "IngestRunRepo.add_ingest failed "
                "(source_path=%s, file_hash=%s)",
                run.source_path,
                run.file_hash,
            )
            raise map_integrity_error(e, ingest_run.name) from e

    def is_already_processed(self, file_hash: str) -> bool:
        try:
            with self._engine.connect() as conn:
                return conn.execute(
                    select(ingest_run)
                    .where(ingest_run.c.file_hash == file_hash)
                ).scalar() is not None
        except IntegrityError as e:
            logger.exception(
                "IngestRunRepo.is_already_processed failed "
                "(file_hash=%s)",
                file_hash,
            )
            raise map_integrity_error(e, ingest_run.name) from e