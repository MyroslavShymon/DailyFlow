import pandas as pd

from daily_flow.analytics.datasets.constants import DatasetPeriod
from daily_flow.analytics.datasets.pipeline import prepare_temporal_data
from daily_flow.analytics.datasets.schema import MOOD_COLUMNS
from daily_flow.analytics.datasets.time_series import analyze_temporal_memory


def get_clean_cross_corr(dfs: dict, target_type: str = "real", max_window: int = 15):
    """
    Your logic is identical:
    1. Loop through each emotion.
    2. Clear the target via exclude_cols.
    3. Calculate windows via analyze_temporal_memory (it already does shift(1)).
    """
    results_list = []

    periods = (
        [DatasetPeriod.FULL]
        if target_type == "real"
        else [DatasetPeriod.FULL, DatasetPeriod.MOODS_ONLY]
    )
    target_col = "common_mood_log" if target_type == "real" else "target_final"

    for emotion in MOOD_COLUMNS:
        # Prepare the target WITHOUT the current emotion (exclude_cols)
        df_clean = prepare_temporal_data(dfs, periods, exclude_cols=[emotion])

        # Remove empty values for correct calculation
        df_clean = df_clean.dropna(subset=[target_col])

        # Calculate correlations (SMA/EWM windows + shift(1) already inside)
        emotion_res = analyze_temporal_memory(
            df_clean, feature_name=emotion, target_name=target_col, max_window=max_window
        )

        # Add a base emotion for further grouping
        emotion_res["emotion_base"] = emotion
        results_list.append(emotion_res)

    return pd.concat(results_list)


def get_critical_features(df_stats, top_n=3):
    """The logic of selecting the top N features for each emotion"""
    df = df_stats.copy().reset_index()

    df["abs_corr"] = df["correlation"].abs()

    critical = (
        df[df["is_significant"]]
        .sort_values(["emotion_base", "abs_corr"], ascending=[True, False])
        .groupby("emotion_base")
        .head(top_n)
    )

    return critical.sort_values("correlation", ascending=False).set_index("feature")
