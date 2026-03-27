import numpy as np
import pandas as pd

from daily_flow.analytics.datasets.schema import BAD_MOOD_COLUMNS, MOOD_COLUMNS


def drop_private_columns(df, columns=None):
    columns = columns or ["note"]
    return df.drop(columns=columns, errors="ignore").copy()


def add_mood_flags(df, mood_fields=None):
    mood_fields = mood_fields or MOOD_COLUMNS
    out = df.copy()
    out["has_common_mood_log"] = out["common_mood_log"].notna()
    out["has_moods"] = out[mood_fields].notna().any(axis=1)
    return out


def add_data_type(df):
    out = df.copy()
    out["data_type"] = np.select(
        [
            out["has_common_mood_log"] & ~out["has_moods"],
            ~out["has_common_mood_log"] & out["has_moods"],
            out["has_common_mood_log"] & out["has_moods"],
        ],
        [
            "common_only",
            "moods_only",
            "both",
        ],
        default="none",
    )
    return out


def calculate_synthetic_mood(df_to_process: pd.DataFrame):
    temp = df_to_process[MOOD_COLUMNS].copy()

    min_mood_val, max_mood_val = 1, 4
    _, max_common_mood_val = 1, 7

    temp[BAD_MOOD_COLUMNS] = (max_mood_val + min_mood_val) - temp[BAD_MOOD_COLUMNS]

    temp[MOOD_COLUMNS] = (temp[MOOD_COLUMNS] - min_mood_val) / (max_mood_val - min_mood_val)

    scaled_total = temp[MOOD_COLUMNS].mean(axis=1)
    return scaled_total * (max_common_mood_val - 1) + 1


def prepare_public_mood_df(df, mood_fields=None):
    out = drop_private_columns(df, columns=["note"])
    out = add_mood_flags(out, mood_fields=mood_fields)
    out = add_data_type(out)
    return out
