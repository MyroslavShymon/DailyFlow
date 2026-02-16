import argparse

from daily_flow.config.db import load_db_settings
from daily_flow.config.paths import INGEST_DATA_DIR
from daily_flow.ingest.cli import build_ingest_cli
from daily_flow.ingest.schemas.common_mood_log import COMMON_MOOD_LOG_INGEST_CONTRACT
from daily_flow.ingest.schemas.mood_log import MOOD_LOG_INGEST_CONTRACT

# common_mood_logs_29_01_2026.csv
# ingest --file mood_logs_05_02_2026.xlsx --dataset mood_log

def main() -> None:
    parser = argparse.ArgumentParser(description="Ingest process")

    parser.add_argument("--file", type=str, required=True, help="The name of the file you want to ingest")
    parser.add_argument("--dataset", type=str, required=True, help="Name of the dataset to load data contract")

    args = parser.parse_args()
    settings = load_db_settings()

    contracts = [MOOD_LOG_INGEST_CONTRACT, COMMON_MOOD_LOG_INGEST_CONTRACT]
    [contract] = [c for c in contracts if c.dataset == args.dataset]
    if not contract:
        raise ValueError("There is no such allowed contract")

    path = INGEST_DATA_DIR / args.file

    build_ingest_cli(
        file_path=path,
        contract=contract,
        db_settings=settings
    )