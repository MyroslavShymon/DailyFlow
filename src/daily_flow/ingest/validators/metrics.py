from typing import TypedDict

import pandas as pd

from daily_flow.ingest.validators.common import ValidationIssue

class BasicMetrics(TypedDict):
    rows_total: int
    file_empty: bool
    rows_bad: int
    rows_good: int
    error_count: int
    warning_count: int
    has_required_columns: bool
    columns_missing_count: int

def get_common_ingest_metrics(
        df: pd.DataFrame,
        bad_row_mask: pd.Series,
        issues: list[ValidationIssue]
) -> BasicMetrics:
    rows_total_count = len(df)
    if not rows_total_count:
        return {
            "rows_total": int(rows_total_count),
            "file_empty": True,
            "rows_bad": 0,
            "rows_good": 0,
            "error_count": 0,
            "warning_count": 0,
            "has_required_columns": False,
            "columns_missing_count": 0,
        }
    else:
        rows_bad_count = bad_row_mask.sum()

        error_count = len({i.code for i in issues if i.severity == 'error'})
        warning_count = len({i.code for i in issues if i.severity == 'warning'})

        return {
            "rows_total": int(rows_total_count),
            "rows_bad": int(rows_bad_count),
            "rows_good": int(rows_total_count - rows_bad_count),

            "error_count": error_count,
            "warning_count": warning_count,

            "has_required_columns": True,
            "columns_missing_count": 0,

            "file_empty": False
        }