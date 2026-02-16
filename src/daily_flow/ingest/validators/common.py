import pandas as pd
from dataclasses import dataclass
from typing import Literal, Any, TypeVar, Generic

from daily_flow.ingest.validators.common_mood_log.definitions import CommonMoodLogValidationErrors, \
    CommonMoodLogValidationWarnings
from daily_flow.ingest.validators.mood_log.definitions import MoodLogValidationErrors, MoodLogValidationWarnings

Severity = Literal["error", "warning"]

ERR = TypeVar("ERR", MoodLogValidationErrors, CommonMoodLogValidationErrors)
WARN = TypeVar("WARN", MoodLogValidationWarnings, CommonMoodLogValidationWarnings)

@dataclass(frozen=True)
class ValidationIssue(Generic[ERR, WARN]):
    code: ERR | WARN              # "missing_day", "out_of_range", "duplicate_key"
    severity: Severity      # "error" або "warning"
    message: str            # людський текст
    count: int              # скільки рядків/значень
    example_index: list[int]  # 3-10 прикладів індексів (не весь список)
    columns: list[str]      # які колонки зачеплені

@dataclass
class ValidationResult(Generic[ERR, WARN]):
    ok: bool
    issues: list[ValidationIssue[ERR, WARN]]
    metrics: dict[str, Any]          # counts/ratios/min/max etc.
    bad_row_mask: pd.Series | None   # bool mask (len == len(df)), якщо хочеш quarantine/skip
    warnings_row_mask: pd.Series | None
