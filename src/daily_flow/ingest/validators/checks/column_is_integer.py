from typing import Optional

import pandas as pd

from daily_flow.ingest.validators.checks.common import CheckResult
from daily_flow.ingest.validators.common import ValidationIssue, ERR


def check_column_is_integer(
        df: pd.DataFrame,
        columns: list[str],
        error_code: ERR,
        message: Optional[str] = None
) -> Optional[CheckResult]:
    has_any_val  = df[columns].notna().any(axis=1)

    is_integer_mask = df[columns].round(0).eq(df[columns]) | df[columns].isna()

    row_is_not_integer = ~is_integer_mask.all(axis=1)
    final_error_mask = row_is_not_integer & has_any_val

    if row_is_not_integer.any():
        issue = ValidationIssue(
            code=error_code,
            severity="error",
            message=message or f"Columns: {', '.join(columns)} can be only integer",
            count=int(row_is_not_integer.sum()),
            example_index=df.index[final_error_mask][:5].tolist(),
            columns=columns
        )

        return {
            "issue": issue,
            "mask": pd.Series(row_is_not_integer).reindex(df.index, fill_value=False)
        }