from typing import Optional

import pandas as pd

from daily_flow.ingest.validators.checks.common import CheckResult
from daily_flow.ingest.validators.common import ValidationIssue, ERR


def check_column_has_any_duplicates(
        df: pd.DataFrame,
        column: str,
        error_code: ERR,
        message: Optional[str] = None
) -> Optional[CheckResult]:
    not_na_columns = df[column].notna()
    all_duplicates = df.duplicated(subset=[column], keep=False)

    duplicates_mask = not_na_columns & all_duplicates

    if duplicates_mask.any():
        issue = ValidationIssue(
            code=error_code,
            severity="error",
            message=message or f"Column '{column}' has duplicates",
            count=int(duplicates_mask.sum()),
            example_index=df.index[duplicates_mask][:5].tolist(),
            columns=[column]
        )

        return {
            "issue": issue,
            "mask": duplicates_mask
        }