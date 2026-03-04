import pandas as pd

from daily_flow.analytics.datasets.schema import COMMON_MOOD_LOGS_DTYPES, MOOD_LOGS_DTYPES


def clean_mood_mart(df: pd.DataFrame) -> pd.DataFrame:
    # забрати дублікати
    df = df.groupby("day", as_index=False).first()

    # вичистити діпазаони
    for mood_log_col in MOOD_LOGS_DTYPES.keys():
        df.loc[~df[mood_log_col].between(1, 4), mood_log_col] = pd.NA

    df.loc[~df["common_mood_log"].between(1, 7), "common_mood_log"] = pd.NA

    # вичистити повністю нульові дні
    cols = [*COMMON_MOOD_LOGS_DTYPES, *MOOD_LOGS_DTYPES]
    empty_mask = df[cols].isna().all(axis=1)

    return df[~empty_mask].copy()
