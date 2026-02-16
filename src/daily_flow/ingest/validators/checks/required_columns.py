from typing import Optional

import pandas as pd
from daily_flow.ingest.validators.common import ValidationIssue, ValidationResult, ERR
from daily_flow.ingest.validators.metrics import BasicMetrics


def check_required_columns(
        df: pd.DataFrame,
        required_columns: tuple[str, ...],
        error: ERR,
) -> Optional[ValidationResult]:
    missing_columns = set(required_columns) - set(df.columns)
    if missing_columns:
        issue = ValidationIssue(
            code=error,
            severity="error",
            message=f"Missing required columns: {', '.join(missing_columns)}",
            count=len(missing_columns),
            example_index=[],
            columns=list(missing_columns)
        )

        metrics: BasicMetrics = {
            "rows_total": int(len(df)),
            "file_empty": len(df) == 0,
            "rows_bad": int(len(df)),
            "rows_good": 0,
            "error_count": 1,
            "warning_count": 0,
            "has_required_columns": False,
            "columns_missing_count": issue.count
        }

        return ValidationResult(
            ok=False,
            issues=[issue],
            bad_row_mask=pd.Series(True, index=df.index),
            warnings_row_mask=pd.Series(False, index=df.index),
            metrics=metrics
        )

