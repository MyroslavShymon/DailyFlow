from datetime import datetime
from pathlib import Path
from typing import Union, Any, Optional

from daily_flow.db.repositories.ingest_run_repo import IngestRunRepo, IngestRun
from daily_flow.db.schema.audit import IngestSourceType, IngestStatusType
from daily_flow.utils.hash import calculate_file_hash


# def ingest_skip_check():І

def ingest_run(
        ingest_run_repo: IngestRunRepo,
        dataset: str,
        source_type: IngestSourceType,
        file_path: Union[str, Path],
        start_time: datetime,
        error_message: Optional[str] = None,
        end_time: Optional[datetime] = None,
        metrics: Optional[dict[str, Any]] = None
) -> Union[IngestRun, bool]:
    path = Path(file_path)
    if not path.is_file():
        raise FileNotFoundError(f"Can't ingest a non-existent file: {file_path}")

    file_hash = calculate_file_hash(path)

    base_params = {
        "dataset": dataset,
        "source_type": source_type,
        "source_path": str(file_path),
        "file_hash": file_hash,
        "started_at": start_time,
    }

    if error_message:
        if end_time is None:
            end_time = datetime.now()

        ingest_run_result = IngestRun(
            **base_params,
            status=IngestStatusType.FAILED,
            error_message=error_message,
            metrics=metrics,
            finished_at=end_time
        )
        return ingest_run_repo.add_ingest(ingest_run_result)


    is_already_ingest = ingest_run_repo.is_already_processed(file_hash)
    if not is_already_ingest and end_time is None:
        return False
    elif is_already_ingest and end_time is None:
        if end_time is None:
            end_time = datetime.now()

        ingest_run_result = IngestRun(
            **base_params,
            status=IngestStatusType.SKIPPED,
            finished_at=end_time,
        )
    else:
        ingest_run_result = IngestRun(
            **base_params,
            status=IngestStatusType.SUCCESS,
            metrics=metrics,
            finished_at=end_time
        )

    return ingest_run_repo.add_ingest(ingest_run_result)