import pandas as pd

from daily_flow.config.paths import INGEST_DATA_DIR
from daily_flow.ingest.schemas.common_mood_log import CommonMoodLogIngestContract, COMMON_MOOD_LOG_INGEST_CONTRACT
from daily_flow.ingest.sources.common_mood_log_csv import read_common_mood_log_csv

COMMON_MOODS = {
    "Awful": 1,
    "Bad": 2,
    "Poor": 3,
    "Neutral": 4,
    "Good": 5,
    "Great": 6,
    "Excellent": 7,
}

def transform_common_mood_log(df_raw:pd.DataFrame, contract: CommonMoodLogIngestContract) -> pd.DataFrame:
    all_columns = contract.required_columns + contract.optional_columns
    df = df_raw[list(all_columns)].copy()

    df = df.loc[~df.isna().all(axis=1)]

    df["note"] = df["note"].astype("string")

    df["day"] = pd.to_datetime(df["day"], errors='coerce')
    df["day"] = df["day"].dt.normalize()

    df["mood"] = df["mood"].map(COMMON_MOODS).astype("int8")

    return df
