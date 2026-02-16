from typing import Optional, Literal

import pandas as pd
from dataclasses import dataclass

@dataclass(frozen=True)
class CleanResult:
    df_clean: pd.DataFrame
    df_quarantine: Optional[pd.DataFrame]
    actions: dict

Mode = Literal["facts", "train"]
BadAction = Literal["fail_fast", "skip", "quarantine"]