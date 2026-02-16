from dataclasses import dataclass
from typing import Union

from daily_flow.db.schema.audit import IngestSourceType
from daily_flow.ingest.schemas.base import BaseIngestContract


@dataclass(frozen=True)
class MoodLogIngestContract(BaseIngestContract):
    mood_columns: tuple[str, ...]
    sheets: Union[tuple[str, ...], None] = None

MOOD_FIELDS = ("joy", "interest", "calm", "energy", "anxiety", "sadness", "irritation", "fatigue", "fear", "confidence", "sleep")

MOOD_LOG_INGEST_CONTRACT = MoodLogIngestContract(
    required_columns=("day",) + MOOD_FIELDS,
    mood_columns=MOOD_FIELDS,
    dataset="mood_log",
    source_type=IngestSourceType.EXCEL
    # sheets=("Жовтень", "Листопад", "Грудень", "Січень"),
)