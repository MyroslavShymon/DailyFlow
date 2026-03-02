import logging

from sqlalchemy.ext.asyncio import AsyncEngine

from daily_flow.db.schema import metadata

logger = logging.getLogger(__name__)


async def init_db(engine: AsyncEngine) -> None:
    async with engine.begin() as conn:
        await conn.run_sync(metadata.create_all)

    if engine.name == "sqlite":
        async with engine.begin() as conn:
            sqlite_master_result = await conn.exec_driver_sql("""
                SELECT name
                FROM sqlite_master
                WHERE type='table'
                  AND name NOT LIKE 'sqlite_%';
            """)
            rows = sqlite_master_result.all()
            db_tables = [row[0] for row in rows]

            if not db_tables:
                raise RuntimeError(
                    "Database file exists but contains no tables or metadata is empty"
                )

            logger.info("Tables in database file: %s", db_tables)

    if (tables_count := len(metadata.tables)) == 0:
        logger.warning("No tables registered in metadata")
    else:
        logger.info("Tables registered in metadata: %d", tables_count)
