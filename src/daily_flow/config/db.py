from dataclasses import dataclass
from dotenv import load_dotenv
import os

from daily_flow.config.paths import ENV_PATH, DATA_DIR


@dataclass(frozen=True)
class DbSettings:
    db_url: str
    auto_init_db: bool = True
    is_sql_echo: bool = True

def load_db_settings() -> DbSettings:
    load_dotenv(ENV_PATH)
    db_file = DATA_DIR / "app.db"
    default_db_url = f"sqlite:///{db_file}"

    db_url = os.getenv("DATABASE_URL", default_db_url)
    auto_init = os.getenv("AUTO_INIT_DB", "1") == "1"
    echo = os.getenv("SQL_ECHO", "1") == "1"

    return DbSettings(db_url=db_url, auto_init_db=auto_init, is_sql_echo=echo)