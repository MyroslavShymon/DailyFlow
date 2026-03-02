from typing import TypedDict

import pandas as pd

from daily_flow.ingest.validators.common import ValidationIssue


class CheckResult(TypedDict):
    issue: ValidationIssue
    mask: pd.Series
