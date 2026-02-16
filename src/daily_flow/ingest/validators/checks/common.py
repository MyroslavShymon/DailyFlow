import pandas as pd
from typing import TypedDict

from daily_flow.ingest.validators.common import ValidationIssue


class CheckResult(TypedDict):
    issue: ValidationIssue
    mask: pd.Series