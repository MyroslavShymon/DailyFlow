import numpy as np
import pandas as pd
from scipy import stats
from statsmodels.tsa.stattools import acf, ccf, pacf

from daily_flow.analytics.datasets.pipeline import prepare_temporal_data
from daily_flow.analytics.datasets.schema import MOOD_COLUMNS


def get_temporal_stats(series, nlags=30):
    N = len(series)
    conf_level = 1.96 / np.sqrt(N)

    acf_vals = acf(series, nlags=nlags)
    pacf_vals = pacf(series, nlags=nlags, method="ols")

    df = pd.DataFrame({"lag": range(len(acf_vals)), "acf": acf_vals, "pacf": pacf_vals})
    df["is_significant"] = df["pacf"].abs() > conf_level
    return df, conf_level


def get_significant_ccf(
    mood_series: pd.Series, feature_series: pd.Series, nlags: int = 15
) -> (np.ndarray, pd.DataFrame, float):
    valid_idx = mood_series.dropna().index
    m = mood_series.loc[valid_idx]
    s = feature_series.loc[valid_idx].fillna(feature_series.median())

    if len(m) == 0:
        return pd.DataFrame()

    corr_values = ccf(m, s, adjusted=False)[:nlags]
    conf_level = 1.96 / np.sqrt(len(m))

    significant_data = []
    for lag, val in enumerate(corr_values):
        if abs(val) > conf_level:
            significant_data.append(
                {
                    "Lag": lag,
                    "Correlation": round(val, 3),
                    "Significant": True,
                    "threshold": round(conf_level, 3),
                }
            )

    return corr_values, pd.DataFrame(significant_data), conf_level


def calculate_feature_lags_matrix(
    dfs: dict, features: list, periods: list, max_lag: int = 15, target_col: str = "target_final"
) -> (pd.DataFrame, float):
    matrix_data = []
    thresholds = []

    for feature in features:
        df_clean = prepare_temporal_data(
            dfs, periods, exclude_cols=feature if feature in MOOD_COLUMNS else None
        )

        corr_values, _, conf_level = get_significant_ccf(
            df_clean[target_col], df_clean[feature], nlags=max_lag + 1
        )

        matrix_data.append(corr_values)
        thresholds.append(conf_level)

    ccf_df = pd.DataFrame(
        matrix_data, index=features, columns=[f"Lag {i}" for i in range(max_lag + 1)]
    )

    avg_conf = np.mean(thresholds)

    return ccf_df, avg_conf


def analyze_temporal_memory(
    df: pd.DataFrame,
    feature_name: str,
    target_name: str,
    max_window: int = 30,
    correlation_method: str = "pearson",
) -> pd.DataFrame:
    """
    Analyzes how past feature values (lags and averages) correlate with the target.
    Helps determine the "depth of memory" of an emotional state.
    """
    analysis_df = df.copy()
    temporal_results = []

    shifted_series = analysis_df[feature_name].shift(1)

    # analysis_df[f'{feature_name}_lag_1'] = shifted_series

    for w in range(1, max_window + 1):
        analysis_df[f"{feature_name}_sma_{w}d"] = shifted_series.rolling(window=w).mean()
        analysis_df[f"{feature_name}_ewm_{w}"] = shifted_series.ewm(span=w).mean()

    temporal_cols = [
        c for c in analysis_df.columns if any(x in c for x in ["_lag_", "_sma_", "_ewm_"])
    ]

    for col in temporal_cols:
        mask = analysis_df[col].notna() & analysis_df[target_name].notna()

        if mask.sum() > 5:
            if correlation_method == "spearman":
                r, p = stats.spearmanr(
                    analysis_df.loc[mask, col], analysis_df.loc[mask, target_name]
                )
            else:
                r, p = stats.pearsonr(
                    analysis_df.loc[mask, col], analysis_df.loc[mask, target_name]
                )

            temporal_results.append(
                {
                    "feature": col,
                    "correlation": r,
                    "p_value": p,
                    # 'n_obs': mask.sum()
                }
            )

    results_df = pd.DataFrame(temporal_results).set_index("feature")
    results_df["is_significant"] = results_df["p_value"] < 0.05

    return results_df.sort_values(by="correlation", ascending=False)
