import pandas as pd

from daily_flow.db.repositories.common_mood_repo import CommonMoodLogRepo, BatchCommonMoodLogUpsertResult, DayPayload


def load_common_mood_log(
        df: pd.DataFrame,
        common_mood_log_repo: CommonMoodLogRepo
) -> BatchCommonMoodLogUpsertResult:
    df_db = df.copy()

    df_db["day"] = pd.to_datetime(df_db["day"]).dt.date
    df_db["note"] = df_db["note"].astype("string")
    df_db["mood"] = df_db["mood"].astype("int8")

    df_payload = df_db.astype(object).where(pd.notnull(df_db), None)

    common_mood_logs_records = df_payload.to_dict(orient='records')

    common_mood_logs_batch_payload: list[DayPayload]  = [
        {
            "day": record.pop("day"),
            "values": record
        } for record in common_mood_logs_records
    ]

    return common_mood_log_repo.batch_upsert_common_mood_logs(payload=common_mood_logs_batch_payload)
