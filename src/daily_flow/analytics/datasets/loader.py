import asyncio

import nest_asyncio
import pandas as pd
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine

from daily_flow.analytics.datasets.clean import clean_mood_mart
from daily_flow.analytics.datasets.mood_mart_sql import MART_QUERY
from daily_flow.analytics.datasets.schema import apply_schema
from daily_flow.config.db import load_db_settings
from daily_flow.db.engine import build_engine


async def _load_mood_mart_df(engine: AsyncEngine) -> pd.DataFrame:
    async with engine.connect() as conn:
        result = await conn.execute(text(MART_QUERY))
        rows = result.fetchall()
        columns = list(result.keys())

    df = pd.DataFrame(rows, columns=columns)

    df = apply_schema(df)
    df = clean_mood_mart(df)

    df = df.sort_values("day")
    df = df.set_index("day")

    return df.copy()


async def _load_mood_mart_async():
    settings = load_db_settings()

    engine = await build_engine(database_url=settings.db_url, is_database_echo=settings.is_sql_echo)

    return await _load_mood_mart_df(engine)


async def load_mood_mart():
    return await _load_mood_mart_async()


def load_mood_mart_sync():
    nest_asyncio.apply()
    return asyncio.run(load_mood_mart())
