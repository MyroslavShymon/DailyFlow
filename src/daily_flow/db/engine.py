import logging

from sqlalchemy import event
from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine

logger = logging.getLogger(__name__)

def build_engine(database_url: str, is_database_echo: bool) -> AsyncEngine:
    logger.info("DATABASE_URL=%s", database_url)

    engine = create_async_engine(
        database_url,
        connect_args={"check_same_thread": False},
        echo=is_database_echo, #виключити ближче ддо деплою
    )

    if database_url.startswith("sqlite"):
        @event.listens_for(engine, "connect")
        def _set_sqlite_pragma(dbapi_connection, connection_record):
            cursor = dbapi_connection.cursor()
            cursor.execute("PRAGMA foreign_keys=ON")
            cursor.execute("PRAGMA journal_mode=WAL")
            cursor.execute("PRAGMA busy_timeout=5000")
            cursor.close()

    with engine.begin() as conn:
        select_check_result = conn.exec_driver_sql("SELECT 1")
        [select_check] = [row[0] for row in select_check_result]

        if select_check == 1:
            logger.info("Select 1 run successfully")

    return engine