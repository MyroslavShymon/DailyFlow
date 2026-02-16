from functools import partial

import pandas as pd

from daily_flow.ingest.schemas.mood_log import MoodLogIngestContract
from daily_flow.ingest.validators.checks.column_has_any_duplicates import check_column_has_any_duplicates
from daily_flow.ingest.validators.checks.column_has_any_na import check_column_has_any_na
from daily_flow.ingest.validators.checks.column_is_integer import check_column_is_integer
from daily_flow.ingest.validators.checks.column_out_of_range import check_column_out_of_range
from daily_flow.ingest.validators.common import ValidationResult
from daily_flow.ingest.validators.engine import _base_validator
from daily_flow.ingest.validators.mood_log.checks.columns_moods_missing import check_columns_moods_missing
from daily_flow.ingest.validators.mood_log.checks.columns_moods_mostly_missing import check_columns_moods_mostly_missing
from daily_flow.ingest.validators.mood_log.checks.columns_only_sleep_filled import check_columns_only_sleep_filled
from daily_flow.ingest.validators.mood_log.definitions import MoodLogValidationErrors, MoodLogValidationWarnings
from daily_flow.ingest.validators.mood_log.metrics import get_mood_log_metrics


def validate_mood_log(df: pd.DataFrame, contract: MoodLogIngestContract) -> ValidationResult[MoodLogValidationErrors, MoodLogValidationWarnings]:
    common_checks = [
        partial(check_column_has_any_na, df, "day", MoodLogValidationErrors.MISSING_DAY),
        partial(check_column_has_any_duplicates, df, "day", MoodLogValidationErrors.DAY_DUPLICATE),
        partial(check_column_out_of_range, df, list(contract.mood_columns), MoodLogValidationErrors.MOOD_IS_OUT_OF_RANGE, 1, 4),
        partial(check_column_is_integer, df, list(contract.mood_columns), MoodLogValidationErrors.MOOD_IS_ONLY_INT),
    ]

    error_checks = [
        partial(check_columns_moods_missing, df, contract),
    ]

    warning_checks = [
        partial(check_columns_moods_mostly_missing, df, contract, 0.5),
        partial(check_columns_only_sleep_filled, df, contract),
    ]

    metrics_call = lambda _df, _errs, _warns, _metrics: get_mood_log_metrics(
        _df, _errs, _warns, contract, _metrics
    )

    return _base_validator(
        df=df,
        contract=contract,
        checks=common_checks,
        metrics_func=metrics_call,
        error_codes_class=MoodLogValidationErrors,
        extra_error_checks=error_checks,
        extra_warning_checks=warning_checks
    )