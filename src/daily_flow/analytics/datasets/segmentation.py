from daily_flow.analytics.datasets.constants import FINAL_DATASET_PERIODS
from daily_flow.analytics.datasets.loader import load_mood_mart_sync
from daily_flow.analytics.datasets.prepare import prepare_public_mood_df


def segment_df(df_to_segment):
    out = df_to_segment.sort_index().copy()

    out["state_change"] = (out["has_moods"] != out["has_moods"].shift()) | (
        out["has_common_mood_log"] != out["has_common_mood_log"].shift()
    )
    out["segment_id"] = out["state_change"].cumsum()

    segmented = (
        out.reset_index()
        .groupby("segment_id")
        .agg(
            start=("day", "min"),
            end=("day", "max"),
            days=("day", "size"),
            has_moods=("has_moods", "first"),
            has_common=("has_common_mood_log", "first"),
        )
    ).copy()

    return out, segmented


def add_sub_segments(df, max_gap_days=5):
    out = df.copy()

    gap = out.index.to_series().groupby(out["segment_id"]).diff().dt.days > max_gap_days

    out["sub_segment"] = gap.groupby(out["segment_id"]).cumsum()

    out["sub_days"] = out.groupby(["segment_id", "sub_segment"]).transform("size")
    return out


def filter_short_sub_segments(df, min_days=7, keep_first=True):
    out = df.copy()

    mask = out["sub_days"] < min_days
    if keep_first:
        mask = mask & (out["sub_segment"] != 0)

    filtered = out.loc[~mask].copy()
    return filtered, mask


def slice_periods(df, periods):
    return {name: df.loc[start:end].copy() for name, (start, end) in periods.items()}


def get_clean_segmented_data():
    raw_df = load_mood_mart_sync()
    initial_df = prepare_public_mood_df(raw_df)

    df, _ = segment_df(initial_df)
    df = add_sub_segments(df, max_gap_days=5)
    filtered_df, _ = filter_short_sub_segments(df, min_days=7, keep_first=True)
    filtered_df, _ = segment_df(filtered_df)

    return initial_df, slice_periods(filtered_df, FINAL_DATASET_PERIODS)
