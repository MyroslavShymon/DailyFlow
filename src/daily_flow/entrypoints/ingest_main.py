import argparse
import asyncio

from daily_flow.config.db import load_db_settings
from daily_flow.config.paths import INGEST_DATA_DIR
from daily_flow.ingest.cli import build_ingest_cli
from daily_flow.ingest.schemas.common_mood_log import COMMON_MOOD_LOG_INGEST_CONTRACT
from daily_flow.ingest.schemas.mood_log import MOOD_LOG_INGEST_CONTRACT

# common_mood_logs_29_01_2026.csv
# ingest --file mood_logs_05_02_2026.xlsx --dataset mood_log


async def main_async() -> None:
    cli, ok = None, None
    try:
        parser = argparse.ArgumentParser(description="Ingest process")

        parser.add_argument(
            "--file", type=str, required=True, help="The name of the file you want to ingest"
        )
        parser.add_argument(
            "--dataset", type=str, required=True, help="Name of the dataset to load data contract"
        )

        args = parser.parse_args()
        settings = load_db_settings()

        contracts = [MOOD_LOG_INGEST_CONTRACT, COMMON_MOOD_LOG_INGEST_CONTRACT]
        contract = next((c for c in contracts if c.dataset == args.dataset), None)
        if contract is None:
            raise ValueError(
                f"Unknown dataset '{args.dataset}'. Allowed: {[c.dataset for c in contracts]}"
            )

        path = INGEST_DATA_DIR / args.file

        cli = await build_ingest_cli(file_path=path, contract=contract, db_settings=settings)
        ok = True
    finally:
        if cli is not None:
            await cli.engine.dispose()
            if ok:
                print("Інжект успішний або вже був здійснений раніше")


def main() -> None:
    asyncio.run(main_async())
