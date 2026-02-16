from typing import TypedDict, cast

import pandas as pd

from daily_flow.ingest.schemas.mood_log import MoodLogIngestContract
from daily_flow.ingest.validators.metrics import BasicMetrics
from daily_flow.ingest.validators.mood_log.definitions import MoodLogValidationErrors, MoodLogValidationWarnings


class MoodLogExtraMetrics(TypedDict):
    unique_days: int
    min_day: str
    max_day: str
    rows_with_any_mood: int
    rows_with_all_moods_missing: int
    rows_out_of_range: int
    rows_non_integer: int
    rows_mostly_empty_moods: int
    rows_sleep_only: int
    rows_missing_day: int
    rows_duplicate_day: int

class MoodLogMetrics(BasicMetrics, MoodLogExtraMetrics):
    pass

def get_mood_log_metrics(
        df: pd.DataFrame,
        error_masks: dict[MoodLogValidationErrors, pd.Series],
        warning_masks: dict[MoodLogValidationWarnings, pd.Series],
        contract: MoodLogIngestContract,
        basic_metrics: BasicMetrics
) -> MoodLogMetrics:
    basic_extra_metrics: MoodLogExtraMetrics = {
        "unique_days": 0,
        "min_day": "",
        "max_day": "",
        "rows_with_any_mood": 0,
        "rows_with_all_moods_missing": 0,
        "rows_out_of_range": 0,
        "rows_non_integer": 0,
        "rows_mostly_empty_moods": 0,
        "rows_sleep_only": 0,
        "rows_missing_day": 0,
        "rows_duplicate_day": 0,
    }
    if basic_metrics["rows_total"] == 0:
        return cast(MoodLogMetrics, {
            **basic_metrics,
            **basic_extra_metrics
        })

    mood_cols_with_value_mask = df[list(contract.mood_columns)].notna().any(axis=1)

    def get_count(key) -> int:
        mask = error_masks.get(key)
        if mask is None:
            mask = warning_masks.get(key)

        return int(mask.sum()) if mask is not None else 0

    min_day = str(df["day"].dropna().min().date())
    max_day = str(df["day"].dropna().max().date())

    return {
        **basic_metrics,

        "unique_days": df["day"].dropna().nunique(),
        "min_day": min_day,
        "max_day": max_day,

        "rows_with_any_mood": int(mood_cols_with_value_mask.sum()),

        "rows_missing_day": get_count(MoodLogValidationErrors.MISSING_DAY),
        "rows_duplicate_day": get_count(MoodLogValidationErrors.DAY_DUPLICATE),
        "rows_out_of_range": get_count(MoodLogValidationErrors.MOOD_IS_OUT_OF_RANGE),
        "rows_non_integer": get_count(MoodLogValidationErrors.MOOD_IS_ONLY_INT),
        "rows_with_all_moods_missing": get_count(MoodLogValidationErrors.NO_MOODS_VALUES),
        "rows_mostly_empty_moods": get_count(MoodLogValidationWarnings.MANY_NAN_MOOD_VALUES),
        "rows_sleep_only": get_count(MoodLogValidationWarnings.SLEEP_ONLY_VALUE),
    }