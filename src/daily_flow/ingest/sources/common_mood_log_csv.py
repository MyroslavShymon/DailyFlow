from pathlib import Path
import pandas as pd


column_mapping = {
    "Time": "day",
    "Mood": "mood",
    "Note": "note"
}

def read_common_mood_log_csv(path: Path) -> pd.DataFrame:
    df = pd.read_csv(
        path,
        encoding='utf-8',
        sep=',',
    )
    df = df.rename(columns=column_mapping)

    return df
