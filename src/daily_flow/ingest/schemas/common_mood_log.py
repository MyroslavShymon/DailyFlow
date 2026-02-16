from dataclasses import dataclass

from daily_flow.db.schema.audit import IngestSourceType
from daily_flow.ingest.schemas.base import BaseIngestContract


@dataclass(frozen=True)
class CommonMoodLogIngestContract(BaseIngestContract):
    optional_columns: tuple[str, ...]

COMMON_MOOD_LOG_INGEST_CONTRACT = CommonMoodLogIngestContract (
    dataset="common_mood_log",
    source_type=IngestSourceType.CSV,
    required_columns=tuple(["day"]),
    optional_columns=("mood", "note")
)