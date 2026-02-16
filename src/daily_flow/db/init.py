import logging
from sqlalchemy.engine import Engine

from daily_flow.db.schema import metadata

logger = logging.getLogger(__name__)

def init_db(engine: Engine) -> None:
    metadata.create_all(engine)

    if engine.name == 'sqlite':
        with engine.begin() as conn:
            sqlite_master_result = conn.exec_driver_sql("""
                SELECT name
                FROM sqlite_master
                WHERE type='table'
                  AND name NOT LIKE 'sqlite_%';
            """)
            db_tables = [row[0] for row in sqlite_master_result]
            if not db_tables:
                raise RuntimeError("Database file exists but contains no tables or metadata is empty")

            logger.info("Tables in database file: %s", db_tables)

    if (tables_count := len(metadata.tables)) == 0:
        logger.warning("No tables registered in metadata")
    else:
        logger.info("Tables registered in metadata: %d", tables_count)
