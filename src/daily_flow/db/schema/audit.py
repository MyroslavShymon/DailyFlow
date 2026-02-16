from enum import StrEnum

from sqlalchemy import Table, Column, Integer, Text, Enum, DateTime, JSON, Index

from .base import metadata

class IngestSourceType(StrEnum):
    EXCEL = "excel"
    CSV = "csv"

class IngestStatusType(StrEnum):
    SUCCESS = "success"
    FAILED = "failed"
    SKIPPED = "skipped"

ingest_run = Table(
    "ingest_run",
    metadata,

    Column(
        "id",
        Integer,
        primary_key=True,
        comment="Unique identifier for the ingestion run"
    ),

    Column(
        "dataset",
        Text,
        nullable=False,
        index=True,  # Added index for faster filtering by dataset name
        comment="Name of the target dataset or table where data is being imported"
    ),

    Column(
        "source_type",
        Enum(IngestSourceType),
        nullable=False,
        comment="Format of the source file (e.g., excel, csv)"
    ),

    Column(
        "source_path",
        Text,
        nullable=False,
        comment="System path or URL to the source file"
    ),

    Column(
        "file_hash",
        Text,
        nullable=False,
        index=True,
        comment="Hash of the file content to prevent redundant processing of the same data"
    ),

    Column(
        "started_at",
        DateTime,
        nullable=False,
        comment="Timestamp when the ingestion process started"
    ),

    Column(
        "finished_at",
        DateTime,
        nullable=False,
        comment="Timestamp when the ingestion process finished or failed"
    ),

    Column(
        "status",
        Enum(IngestStatusType),
        nullable=False,
        comment="Current execution state: success, failed, or skipped"
    ),

    Column(
        "metrics",
        JSON,
        nullable=True,
        comment="Execution metadata and metrics (e.g., row count, processing stats)"
    ),

    Column(
        "error_message",
        Text,
        nullable=True,
        comment="Detailed error description or traceback if the status is FAILED"
    )
)
