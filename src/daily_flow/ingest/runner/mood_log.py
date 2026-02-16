from datetime import datetime
from pathlib import Path
from typing import Union

from daily_flow.db.repositories.ingest_run_repo import IngestRunRepo
from daily_flow.db.repositories.mood_log_repo import MoodLogRepo
from daily_flow.db.schema.audit import IngestStatusType
from daily_flow.ingest.audit.ingest_run import ingest_run
from daily_flow.ingest.cleaning.policies import apply_validation_policy
from daily_flow.ingest.loaders.mood_log import load_mood_log
from daily_flow.ingest.schemas.mood_log import MoodLogIngestContract 
from daily_flow.ingest.sources.mood_log_excel import read_mood_log_excel
from daily_flow.ingest.transforms.mood_log import normalize_mood_log
from daily_flow.ingest.validators.mood_log.validator import validate_mood_log


def mood_log_runner(
        file_path: Union[str, Path],
        contract: MoodLogIngestContract ,
        ingest_run_repo: IngestRunRepo,
        mood_log_repo: MoodLogRepo,
) -> IngestStatusType:
    base_ingest_params = {
        "dataset": contract.dataset,
        "source_type": contract.source_type,
        "start_time": datetime.now(),
        "file_path": file_path,
        "ingest_run_repo": ingest_run_repo,
    }

    result_metrics = None

    try:
        ingest_result = ingest_run(**base_ingest_params)
        if ingest_result and ingest_result.status == IngestStatusType.SKIPPED:
            return IngestStatusType.SKIPPED

        read_result = read_mood_log_excel(file_path, contract)
        normalized_result = normalize_mood_log(read_result, contract)

        validation_result = validate_mood_log(normalized_result, contract)
        print(f"{validation_result=}")
        result_metrics = validation_result.metrics

        clean_result = apply_validation_policy(
            df=normalized_result,
            validation_report=validation_result,
            mode="train",
            bad_action="quarantine"
        )

        batch_upsert_result = load_mood_log(
            df=clean_result.df_clean,
            contract=contract,
            mood_log_repo=mood_log_repo
        )

        if batch_upsert_result:
            return ingest_run(
                **base_ingest_params,
                end_time=datetime.now(),
                metrics=result_metrics
            ).status
    except Exception as e:
        end_time = datetime.now()
        msg = str(getattr(e, "orig", e)).lower()

        return ingest_run(
            **base_ingest_params,
            end_time=end_time,
            error_message=msg,
            metrics=result_metrics
        ).status