import pandas as pd
from scipy.stats import pearsonr

from daily_flow.analytics.datasets.prepare import calculate_synthetic_mood
from daily_flow.analytics.datasets.schema import BAD_MOOD_COLUMNS, FACTORS, MOOD_COLUMNS


def prepare_temporal_data(
    dfs,
    dataset_periods,
    exclude_cols=None,
    factors_to_exclude=None,
    mood_columns=MOOD_COLUMNS,
    bad_mood_columns=BAD_MOOD_COLUMNS,
):
    if factors_to_exclude is None:
        factors_to_exclude = FACTORS

    df_to_process = pd.concat([dfs[p] for p in dataset_periods]).sort_index()

    if exclude_cols is None:
        exclude_cols = []
    elif isinstance(exclude_cols, str):
        exclude_cols = [exclude_cols]

    current_mood_cols = [
        c for c in mood_columns if c not in exclude_cols and c not in factors_to_exclude
    ]
    current_bad_cols = [
        c for c in bad_mood_columns if c not in exclude_cols and c not in factors_to_exclude
    ]

    if df_to_process["target_modeled"].notna().any():
        df_to_process["target_final"] = (
            df_to_process["common_mood_log"].astype(float).fillna(df_to_process["target_modeled"])
        )
        return df_to_process

    df_to_process["total_mood_synthetic"] = calculate_synthetic_mood(
        df_to_process, columns_to_process=current_mood_cols, bad_columns_to_process=current_bad_cols
    )

    df_to_process["target_final"] = (
        df_to_process["common_mood_log"].astype(float).fillna(df_to_process["total_mood_synthetic"])
    )

    return df_to_process


def validate_synthetic_logic(dfs: dict, target_period) -> pd.DataFrame:
    results = []
    df_full = dfs[target_period].copy()
    y_true = df_full["common_mood_log"].astype(float)

    test_emotions = [c for c in MOOD_COLUMNS if c not in FACTORS]

    for emotion in test_emotions:
        df_temp = prepare_temporal_data(
            dfs, [target_period], exclude_cols=emotion, factors_to_exclude=FACTORS
        )
        y_synth = df_temp["total_mood_synthetic"]

        mask = y_true.notna() & y_synth.notna()
        if mask.sum() < 2:
            continue

        r_coef, p_val = pearsonr(y_true[mask], y_synth[mask])

        results.append(
            {
                "Excluded_Emotion": emotion,
                "Correlation_r": round(r_coef, 3),
                "P_value": round(p_val, 4),
                "Status": "✅ Stable" if p_val < 0.05 and r_coef > 0.6 else "⚠️ Volatile",
            }
        )

    return pd.DataFrame(results).sort_values(by="Correlation_r", ascending=False)
