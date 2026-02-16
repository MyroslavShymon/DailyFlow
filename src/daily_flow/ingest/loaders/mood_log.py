import pandas as pd

from daily_flow.db.repositories.mood_log_repo import MoodLogRepo, DayPayload, BatchMoodLogUpsertResult
from daily_flow.ingest.schemas.mood_log import MoodLogIngestContract 

def load_mood_log(
        df: pd.DataFrame,
        contract: MoodLogIngestContract ,
        mood_log_repo: MoodLogRepo,
) -> BatchMoodLogUpsertResult:
    df_db = df.copy()

    df_db = df_db.astype({mood_column: "Int8" for mood_column in contract.mood_columns})

    df_db["day"] = pd.to_datetime(df_db["day"]).dt.date

    df_payload = df_db.astype(object).where(pd.notnull(df_db), None)

    mood_logs_records = df_payload.to_dict(orient='records')

    print(f"{mood_logs_records=}")

    mood_logs_batch_payload: list[DayPayload]  = [
        {
            "day": record.pop("day"),
            "values": record
        } for record in mood_logs_records
    ]

    return mood_log_repo.batch_upsert_mood_logs(payload=mood_logs_batch_payload)

