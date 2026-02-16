import pandas as pd

from daily_flow.ingest.schemas.mood_log import MoodLogIngestContract

def transform_mood_log_sheet(df_raw: pd.DataFrame, contract: MoodLogIngestContract ) -> pd.DataFrame:
    df = df_raw[list(contract.required_columns)].copy()

    df = df.loc[~df.isna().all(axis=1)]

    df["day"] = pd.to_datetime(df["day"], errors='coerce')

    for mood_col in contract.mood_columns:
        df[mood_col] = pd.to_numeric(df[mood_col], errors='coerce')
        df[mood_col] = df[mood_col].astype('Float64')

    return df

def normalize_mood_log(df_raws: list[dict[str, pd.DataFrame | str]], contract: MoodLogIngestContract ) -> pd.DataFrame:
    sheets = []

    for df_raw in df_raws:
        sheet = transform_mood_log_sheet(
            df_raw=df_raw["sheet"],
            contract=contract
        )
        sheets.append(sheet)

    df = pd.concat(sheets)
    df = df.reset_index(drop=True)
    return df
