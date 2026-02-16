from datetime import datetime
from pathlib import Path
from typing import Union

from daily_flow.db.repositories.common_mood_repo import CommonMoodLogRepo
from daily_flow.db.repositories.ingest_run_repo import IngestRunRepo
from daily_flow.db.schema.audit import IngestStatusType
from daily_flow.ingest.audit.ingest_run import ingest_run
from daily_flow.ingest.cleaning.policies import apply_validation_policy
from daily_flow.ingest.loaders.common_mood_log import load_common_mood_log
from daily_flow.ingest.schemas.common_mood_log import CommonMoodLogIngestContract
from daily_flow.ingest.sources.common_mood_log_csv import read_common_mood_log_csv
from daily_flow.ingest.transforms.common_mood_log import transform_common_mood_log
from daily_flow.ingest.validators.common_mood_log.validator import validate_common_mood_log


def common_mood_log_runner(
        file_path: Union[str, Path],
        contract: CommonMoodLogIngestContract,
        ingest_run_repo: IngestRunRepo,
        common_mood_log_repo: CommonMoodLogRepo
):
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

        read_result = read_common_mood_log_csv(file_path)
        transformed_result = transform_common_mood_log(read_result, contract)

        validation_result= validate_common_mood_log(transformed_result, contract)
        result_metrics = validation_result.metrics

        clean_result = apply_validation_policy(
            df=transformed_result,
            validation_report=validation_result,
            mode="train",
            bad_action="quarantine"
        )

        batch_upsert_result = load_common_mood_log(
            df=clean_result.df_clean,
            common_mood_log_repo=common_mood_log_repo
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



