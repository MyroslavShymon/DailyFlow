from typing import Optional

import pandas as pd

from daily_flow.ingest.schemas.common_mood_log import CommonMoodLogIngestContract
from daily_flow.ingest.validators.checks.common import CheckResult
from daily_flow.ingest.validators.common import ValidationIssue
from daily_flow.ingest.validators.common_mood_log.definitions import CommonMoodLogValidationWarnings


def check_column_has_no_optional_fields(
        df: pd.DataFrame,
        contract: CommonMoodLogIngestContract,
) -> Optional[CheckResult]:
    optional_columns = list(contract.optional_columns)
    has_no_optional_fields = df[optional_columns].isna().all(axis=1)
    if has_no_optional_fields.any():
        issue = ValidationIssue(
            code=CommonMoodLogValidationWarnings.NO_OPTIONAL_FIELDS,
            severity="warning",
            message="There are no optional fields in raw",
            count=has_no_optional_fields.sum(),
            example_index=df.index[has_no_optional_fields][:5].tolist(),
            columns=optional_columns
        )
        return {
            "issue": issue,
            "mask": pd.Series(has_no_optional_fields).reindex(df.index, fill_value=False)
        }
