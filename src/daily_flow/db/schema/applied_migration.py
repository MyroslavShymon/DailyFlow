from sqlalchemy import Table, Column, Integer, UniqueConstraint, CheckConstraint, DateTime, Text, text

from .base import metadata

applied_migration = Table(
    "applied_migration",
    metadata,

    Column(
        "id",
        Integer,
        primary_key=True,
        comment="Unique migration identifier"
    ),

    Column(
        "version",
        Integer,
        nullable=False,
        comment="Version of the project"
    ),
    Column(
        "migration_name",
        Text,
        nullable=False,
        comment="Name of the migration"
    ),
    Column(
        "applied_at",
        DateTime,
        nullable=False,
        server_default=text("CURRENT_TIMESTAMP"),
        comment="Date time when migration was applied."
    ),

    UniqueConstraint("version", name="uq_migration_version"),
    UniqueConstraint("migration_name", name="uq_migration_name"),

    CheckConstraint("length(migration_name) > 0", name="ck_migration_name_not_empty"),

    comment="History of applied schema migrations"
)