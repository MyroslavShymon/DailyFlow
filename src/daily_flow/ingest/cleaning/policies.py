from typing import get_args

import pandas as pd

from daily_flow.ingest.cleaning.common import CleanResult, Mode, BadAction
from daily_flow.ingest.validators.common import ValidationResult


def apply_validation_policy(
        df: pd.DataFrame,
        validation_report: ValidationResult,
        mode: Mode = "facts",
        bad_action: BadAction = "quarantine"
) -> CleanResult:
    allowed_modes, allowed_bad_actions = get_args(Mode), get_args(BadAction)
    if mode not in allowed_modes:
        raise ValueError(f"Invalid mode: {mode}. Allowed: {allowed_modes}")
    if bad_action not in allowed_bad_actions:
        raise ValueError(f"Invalid bad action: {bad_action}. Allowed: {allowed_bad_actions}")

    bad_count = int(validation_report.bad_row_mask.sum())
    warn_count = int(validation_report.warnings_row_mask.sum())

    if bad_count > 0 and bad_action == "fail_fast":
        raise ValueError(
            f"Validation failed: {bad_count} bad rows (errors). "
            f"Mode={mode}. Consider bad_action='quarantine' or 'skip'."
        )

    if bad_action == "skip":
        df_clean = df[~validation_report.bad_row_mask].copy()
        df_quarantine = None
    elif bad_action == "quarantine":
        df_clean = df[~validation_report.bad_row_mask].copy()
        df_quarantine = df[validation_report.bad_row_mask].copy()
    else:
        df_clean = df.copy()
        df_quarantine = None

    if mode == "train":
        df_clean = df_clean.loc[~validation_report.warnings_row_mask.reindex(df_clean.index, fill_value=False)].copy()

    actions = {
        "mode": mode,
        "bad_action": bad_action,
        "rows_in": int(len(df)),
        "rows_bad": bad_count,
        "rows_warn": warn_count,
        "rows_out": int(len(df_clean)),
        "rows_quarantine": int(len(df_quarantine)) if df_quarantine is not None else 0,
    }

    return CleanResult(
        df_clean=df_clean,
        df_quarantine=df_quarantine,
        actions=actions
    )