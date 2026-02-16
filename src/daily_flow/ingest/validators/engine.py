from typing import Type, Callable

import pandas as pd

from daily_flow.ingest.schemas.base import BaseIngestContract
from daily_flow.ingest.validators.checks.required_columns import check_required_columns
from daily_flow.ingest.validators.common import ValidationIssue, ValidationResult, ERR, WARN
from daily_flow.ingest.validators.metrics import get_common_ingest_metrics


def _base_validator(
        df: pd.DataFrame,
        contract: BaseIngestContract,
        checks: list[Callable],
        metrics_func: Callable,
        error_codes_class: Type[ERR],
        extra_error_checks: list[Callable] = None,
        extra_warning_checks: list[Callable] = None,
) -> ValidationResult[ERR, WARN]:
    if check_required_res := check_required_columns(
        df,
        contract.required_columns,
        error_codes_class.MISSING_REQUIRED_COLUMNS
    ):
        return check_required_res

    issues: list[ValidationIssue[ERR, WARN]] = []
    bad_row_mask = pd.Series(False, index=df.index)
    warnings_row_mask = pd.Series(False, index=df.index)
    error_masks: dict[ERR, pd.Series] = {}
    warning_masks: dict[WARN, pd.Series] = {}

    all_error_checks = checks + (extra_error_checks or [])
    for check_func in all_error_checks:
        if res := check_func():
            issue, mask = res["issue"], res["mask"]

            error_masks[issue.code] = mask

            issues.append(issue)
            bad_row_mask |= mask

    for warn_func in (extra_warning_checks or []):
        if res := warn_func():
            issue, mask = res["issue"], res["mask"]

            warning_masks[issue.code] = mask

            issues.append(issue)
            warnings_row_mask  |= mask

    basic_metrics = get_common_ingest_metrics(
        df=df,
        bad_row_mask=bad_row_mask,
        issues=issues
    )

    metrics = metrics_func(
        df,
        error_masks,
        warning_masks,
        basic_metrics
    )

    return ValidationResult(
        ok=not bad_row_mask.any(),
        issues=issues,
        bad_row_mask=bad_row_mask,
        warnings_row_mask=warnings_row_mask,
        metrics=metrics
    )



