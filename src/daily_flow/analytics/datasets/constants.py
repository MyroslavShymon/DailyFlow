from enum import Enum


class DatasetPeriod(Enum):
    COMMON_ONLY = "common_only"
    MOODS_ONLY = "moods_only"
    FULL = "full"


FINAL_DATASET_PERIODS = {
    DatasetPeriod.COMMON_ONLY: ("2025-01-03", "2025-05-04"),
    DatasetPeriod.MOODS_ONLY: ("2025-10-06", "2025-12-31"),
    DatasetPeriod.FULL: ("2026-01-01", "2026-03-19"),
}
