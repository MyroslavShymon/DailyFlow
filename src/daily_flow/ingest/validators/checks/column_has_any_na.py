from typing import Optional

import pandas as pd

from daily_flow.ingest.validators.checks.common import CheckResult
from daily_flow.ingest.validators.common import ValidationIssue, ERR


def check_column_has_any_na(
        df: pd.DataFrame,
        column: str,
        error_code: ERR,
        message: Optional[str] = None
) -> Optional[CheckResult]:
    na_mask = df[column].isna()

    if na_mask.any():
        issue = ValidationIssue(
            code=error_code,
            severity="error",
            message=message or f"Column '{column}' has missing values",
            count=int(na_mask.sum()),
            example_index=df.index[na_mask][:5].tolist(),
            columns=[column]
        )

        return {
            "issue": issue,
            "mask": na_mask
        }