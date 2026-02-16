from dataclasses import dataclass

from daily_flow.db.schema.audit import IngestSourceType


@dataclass(frozen=True)
class BaseIngestContract:
    required_columns: tuple[str, ...]
    dataset: str
    source_type: IngestSourceType