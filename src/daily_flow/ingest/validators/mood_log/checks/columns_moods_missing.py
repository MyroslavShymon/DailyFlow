from typing import Optional

import pandas as pd

from daily_flow.ingest.schemas.mood_log import MoodLogIngestContract
from daily_flow.ingest.validators.checks.common import CheckResult
from daily_flow.ingest.validators.common import ValidationIssue
from daily_flow.ingest.validators.mood_log.definitions import MoodLogValidationErrors


def check_columns_moods_missing(
        df: pd.DataFrame,
        contract: MoodLogIngestContract
) -> Optional[CheckResult]:
    mood_columns = list(contract.mood_columns)
    mood_cols_na_mask = df[mood_columns].isna().all(axis=1)

    if mood_cols_na_mask.any():
        issue = ValidationIssue(
            code=MoodLogValidationErrors.NO_MOODS_VALUES,
            severity="error",
            message="All of mood columns haven't any value",
            count=int(mood_cols_na_mask.sum()),
            example_index=df.index[mood_cols_na_mask][:5].tolist(),
            columns=mood_columns
        )
        return {
            "issue": issue,
            "mask": mood_cols_na_mask
        }
