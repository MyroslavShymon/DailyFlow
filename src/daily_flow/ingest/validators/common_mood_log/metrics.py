from typing import TypedDict, cast

import pandas as pd

from daily_flow.ingest.validators.common_mood_log.definitions import CommonMoodLogValidationWarnings, \
    CommonMoodLogValidationErrors
from daily_flow.ingest.validators.metrics import BasicMetrics


class CommonMoodLogExtraMetrics(TypedDict):
    unique_days: int
    min_day: str
    max_day: str
    rows_out_of_range: int
    rows_non_integer: int
    rows_missing_day: int
    rows_duplicate_day: int
    rows_with_no_optional_fields: int

class CommonMoodLogMetrics(BasicMetrics, CommonMoodLogExtraMetrics):
    pass

def get_common_mood_log_metrics(
        df: pd.DataFrame,
        error_masks: dict[CommonMoodLogValidationErrors, pd.Series],
        warning_masks: dict[CommonMoodLogValidationWarnings, pd.Series],
        basic_metrics: BasicMetrics
):
    basic_extra_metrics: CommonMoodLogExtraMetrics = {
        "unique_days": 0,
        "min_day": "",
        "max_day": "",
        "rows_out_of_range": 0,
        "rows_non_integer": 0,
        "rows_missing_day": 0,
        "rows_duplicate_day": 0,
        "rows_with_no_optional_fields": 0,
    }
    if basic_metrics["rows_total"] == 0:
        return cast(CommonMoodLogMetrics, {
            **basic_metrics,
            **basic_extra_metrics
        })

    min_day = str(df["day"].dropna().min().date())
    max_day = str(df["day"].dropna().max().date())


    def get_count(key) -> int:
        mask = error_masks.get(key)
        if mask is None:
            mask = warning_masks.get(key)

        return int(mask.sum()) if mask is not None else 0

    return {
        **basic_metrics,

        "unique_days": df["day"].dropna().nunique(),
        "min_day": min_day,
        "max_day": max_day,

        "rows_out_of_range": get_count(CommonMoodLogValidationErrors.MOOD_IS_OUT_OF_RANGE),
        "rows_non_integer": get_count(CommonMoodLogValidationErrors.MOOD_IS_ONLY_INT),
        "rows_missing_day": get_count(CommonMoodLogValidationErrors.MISSING_DAY),
        "rows_duplicate_day": get_count(CommonMoodLogValidationErrors.DAY_DUPLICATE),
        "rows_with_no_optional_fields": get_count(CommonMoodLogValidationWarnings.NO_OPTIONAL_FIELDS),
    }

