import logging
from pathlib import Path
import pandas as pd

from daily_flow.ingest.schemas.mood_log import MoodLogIngestContract

logger = logging.getLogger(__name__)

column_mapping = {
    "дата": "day",
    "Радість": "joy",
    "Зацікавлення": "interest",
    "Спокій": "calm",
    "Енергійність": "energy",
    "Тривога": "anxiety",
    "Засмучення": "sadness",
    "Роздратування": "irritation",
    "Втома": "fatigue",
    "Страх": "fear",
    "Впевненість": "confidence",
    "Сон": "sleep",
}

def read_mood_log_excel(path: Path, contract: MoodLogIngestContract) -> list[dict[str, pd.DataFrame | str]]:
    all_sheets = pd.read_excel(
        path,
        sheet_name=contract.sheets or None,
        engine="openpyxl",
        header=[0]
    )

    if not contract.sheets and isinstance(all_sheets, dict):
        all_sheets = {
            name: df
            for name, df in all_sheets.items()
            if len(set(column_mapping.keys()) - set(df.columns.tolist())) == 0
        }

    if not all_sheets:
        raise ValueError("Incorrect sheets count or excel file")

    dfs_sheets = []
    for sheet_name, df in all_sheets.items():
        df = df.rename(columns=column_mapping)
        dfs_sheets.append({"sheet_name": sheet_name, "sheet": df})
    return dfs_sheets
