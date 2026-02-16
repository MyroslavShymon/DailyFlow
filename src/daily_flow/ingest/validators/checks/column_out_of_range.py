from typing import Optional

import pandas as pd

from daily_flow.ingest.validators.checks.common import CheckResult
from daily_flow.ingest.validators.common import ValidationIssue, ERR


def check_column_out_of_range(
    df: pd.DataFrame,
    columns: list[str],
    error_code: ERR,
    min_val: int,
    max_val: int,
    message: Optional[str] = None
) -> Optional[CheckResult]:
    raw_has_any_val = df[columns].notna().any(axis=1)

    in_range_or_na = (df[columns].ge(min_val) & df[columns].le(max_val)) | df[columns].isna()
    column_range_bad = ~(in_range_or_na.all(axis=1)) & raw_has_any_val

    if column_range_bad.any():
        issue = ValidationIssue(
            code=error_code,
            severity="error",
            message=message or f"Columns: {', '.join(columns)} are out of range {min_val} - {max_val}",
            count=int(column_range_bad.sum()),
            example_index=df.index[column_range_bad][:5].tolist(),
            columns=columns
        )

        return  {
            "issue": issue,
            "mask": column_range_bad
        }
