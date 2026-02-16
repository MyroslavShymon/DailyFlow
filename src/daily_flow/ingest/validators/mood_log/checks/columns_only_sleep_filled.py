from typing import Optional

import pandas as pd

from daily_flow.ingest.schemas.mood_log import MoodLogIngestContract
from daily_flow.ingest.validators.checks.common import CheckResult
from daily_flow.ingest.validators.common import ValidationIssue
from daily_flow.ingest.validators.mood_log.definitions import MoodLogValidationWarnings


def check_columns_only_sleep_filled(
        df: pd.DataFrame,
        contract: MoodLogIngestContract
) -> Optional[CheckResult]:
    mood_columns = list(contract.mood_columns)
    mood_without_sleep = [c for c in mood_columns if c != "sleep"]

    has_any_mood = df[mood_columns].notna().any(axis=1)

    all_moods_empty  = df[mood_without_sleep].isna().all(axis=1)
    sleep_not_empty  = df["sleep"].notna()

    sleep_only_mask  = has_any_mood & all_moods_empty & sleep_not_empty
    if sleep_only_mask.any():
        issue = ValidationIssue(
            code=MoodLogValidationWarnings.SLEEP_ONLY_VALUE,
            severity="warning",
            message="There is only sleep value without other moods",
            count=int(sleep_only_mask.sum()),
            example_index=df.index[sleep_only_mask][:5].tolist(),
            columns=mood_without_sleep
        )

        return {
            "issue": issue,
            "mask": sleep_only_mask
        }