from functools import partial

import pandas as pd

from daily_flow.ingest.schemas.common_mood_log import CommonMoodLogIngestContract
from daily_flow.ingest.validators.checks.column_has_any_duplicates import check_column_has_any_duplicates
from daily_flow.ingest.validators.checks.column_has_any_na import check_column_has_any_na
from daily_flow.ingest.validators.checks.column_is_integer import check_column_is_integer
from daily_flow.ingest.validators.checks.column_out_of_range import check_column_out_of_range
from daily_flow.ingest.validators.checks.required_columns import check_required_columns
from daily_flow.ingest.validators.common import ValidationIssue, ValidationResult
from daily_flow.ingest.validators.common_mood_log.checks.column_has_no_optional_fields import \
    check_column_has_no_optional_fields
from daily_flow.ingest.validators.common_mood_log.definitions import CommonMoodLogValidationErrors, \
    CommonMoodLogValidationWarnings
from daily_flow.ingest.validators.common_mood_log.metrics import get_common_mood_log_metrics
from daily_flow.ingest.validators.engine import _base_validator
from daily_flow.ingest.validators.metrics import get_common_ingest_metrics


def validate_common_mood_log(df: pd.DataFrame, contract: CommonMoodLogIngestContract) -> ValidationResult[CommonMoodLogValidationErrors, CommonMoodLogValidationWarnings]:
    common_checks = [
        partial(check_column_has_any_na, df, "day", CommonMoodLogValidationErrors.MISSING_DAY),
        partial(check_column_has_any_duplicates, df, "day", CommonMoodLogValidationErrors.DAY_DUPLICATE),
        partial(check_column_out_of_range, df, ["mood"], CommonMoodLogValidationErrors.MOOD_IS_OUT_OF_RANGE, 1, 7),
        partial(check_column_is_integer,df, ["mood"], CommonMoodLogValidationErrors.MOOD_IS_ONLY_INT),
    ]

    warning_checks = [
        partial(check_column_has_no_optional_fields, df, contract),
    ]

    return _base_validator(
        df=df,
        contract=contract,
        checks=common_checks,
        metrics_func=get_common_mood_log_metrics,
        error_codes_class=CommonMoodLogValidationErrors,
        extra_warning_checks=warning_checks
    )