from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[3]
DAILY_FLOW_DIR = Path(__file__).resolve().parents[1]

DATA_DIR = BASE_DIR / "data"
ENV_PATH = BASE_DIR / ".env"

INGEST_DATA_DIR = DAILY_FLOW_DIR / "data"
