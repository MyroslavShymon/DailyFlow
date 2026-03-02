from dataclasses import dataclass
from typing import Literal

import pandas as pd


@dataclass(frozen=True)
class CleanResult:
    df_clean: pd.DataFrame
    df_quarantine: pd.DataFrame | None
    actions: dict


Mode = Literal["facts", "train"]
BadAction = Literal["fail_fast", "skip", "quarantine"]
