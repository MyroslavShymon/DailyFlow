import numpy as np

from daily_flow.analytics.datasets.schema import MOOD_COLUMNS


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


def prepare_public_mood_df(df, mood_fields=None):
    out = drop_private_columns(df, columns=["note"])
    out = add_mood_flags(out, mood_fields=mood_fields)
    out = add_data_type(out)
    return out
