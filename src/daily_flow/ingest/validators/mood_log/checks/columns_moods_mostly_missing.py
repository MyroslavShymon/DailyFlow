from typing import Optional

import pandas as pd

from daily_flow.ingest.schemas.mood_log import MoodLogIngestContract
from daily_flow.ingest.validators.checks.common import CheckResult
from daily_flow.ingest.validators.common import ValidationIssue
from daily_flow.ingest.validators.mood_log.definitions import MoodLogValidationWarnings


def check_columns_moods_mostly_missing(
        df: pd.DataFrame,
        contract: MoodLogIngestContract,
        threshold: float = 0.5
) -> Optional[CheckResult]:
    mood_columns = list(contract.mood_columns)

    mood_without_sleep = [c for c in mood_columns if c != "sleep"]

    mostly_empty_mask = pd.Series(
        df[mood_without_sleep].isna().mean(axis=1) > threshold,
        index=df.index
    )
    if mostly_empty_mask.any():
        issue = ValidationIssue(
            code=MoodLogValidationWarnings.MANY_NAN_MOOD_VALUES,
            severity="warning",
            message=f"More than {int(threshold*100)}% of mood values are empty",
            count=int(mostly_empty_mask.sum()),
            example_index=df.index[mostly_empty_mask][:5].tolist(),
            columns=mood_columns
        )
        return {
            "issue": issue,
            "mask": mostly_empty_mask
        }
