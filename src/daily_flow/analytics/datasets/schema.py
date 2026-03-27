import pandas as pd

MOOD_LOGS_DTYPES = {
    "joy": "UInt8",
    "interest": "UInt8",
    "calm": "UInt8",
    "energy": "UInt8",
    "anxiety": "UInt8",
    "sadness": "UInt8",
    "irritation": "UInt8",
    "fatigue": "UInt8",
    "fear": "UInt8",
    "confidence": "UInt8",
    "sleep": "UInt8",
}

COMMON_MOOD_LOGS_DTYPES = {
    "common_mood_log": "UInt8",
    "note": "string",
}

DTYPES = {**COMMON_MOOD_LOGS_DTYPES, **MOOD_LOGS_DTYPES}

REQUIRED_COLUMNS = ["day"]
MOOD_COLUMNS = list(MOOD_LOGS_DTYPES.keys())
GOOD_MOOD_COLUMNS = ["joy", "interest", "calm", "energy", "confidence", "sleep"]
BAD_MOOD_COLUMNS = ["anxiety", "sadness", "irritation", "fatigue", "fear"]


def apply_schema(df: pd.DataFrame) -> pd.DataFrame:
    for req_col in REQUIRED_COLUMNS:
        if req_col not in df.columns:
            raise ValueError(f"Column {req_col} is required")

    df["day"] = pd.to_datetime(df["day"], errors="coerce")

    for col, col_type in DTYPES.items():
        if col in df.columns:
            df[col] = df[col].astype(col_type)

    return df.copy()
