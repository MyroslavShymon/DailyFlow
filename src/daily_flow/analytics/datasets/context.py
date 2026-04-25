import pandas as pd

from daily_flow.analytics.datasets.constants import AnalysisProfiles, DatasetPeriod


def get_mood_target_analysis_profiles(
    dfs: dict[DatasetPeriod, pd.DataFrame], df_temp: pd.DataFrame
) -> dict[AnalysisProfiles, pd.Series]:
    return {
        AnalysisProfiles.HISTORICAL: dfs[DatasetPeriod.COMMON_ONLY]["common_mood_log"].dropna(),
        AnalysisProfiles.SYNTHETIC_BRIDGE: df_temp["target_final"].dropna(),
        AnalysisProfiles.MODERN_FULL: dfs[DatasetPeriod.FULL]["common_mood_log"].dropna(),
    }


def get_mood_analysis_profiles(
    dfs: dict[DatasetPeriod, pd.DataFrame], df_temp: pd.DataFrame
) -> dict[AnalysisProfiles, pd.DataFrame]:
    return {
        AnalysisProfiles.HISTORICAL: dfs[DatasetPeriod.COMMON_ONLY],
        AnalysisProfiles.SYNTHETIC_BRIDGE: df_temp,
        AnalysisProfiles.MODERN_FULL: dfs[DatasetPeriod.FULL],
    }


def get_sleep_impact_profiles(
    dfs: dict[DatasetPeriod, pd.DataFrame], df_temp: pd.DataFrame
) -> dict[AnalysisProfiles, tuple]:
    return {
        AnalysisProfiles.MODERN_FULL: (
            dfs[DatasetPeriod.FULL]["common_mood_log"],
            dfs[DatasetPeriod.FULL]["sleep"],
        ),
        AnalysisProfiles.SYNTHETIC_BRIDGE: (df_temp["target_final"], df_temp["sleep"]),
    }
