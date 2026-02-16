from sqlalchemy import Table, Column, Integer, Date, Text, CheckConstraint, DateTime, UniqueConstraint, text, ForeignKey

from .base import metadata

common_mood_log = Table(
    "common_mood_log",
    metadata,

Column(
        "id",
        Integer,
        primary_key=True,
        comment = "Unique entry identifier."
    ),

    # One general comment
    Column(
        "note",
        Text,
        nullable=True,
        comment = "One short note about the day (optional)."
    ),

    # What day is the assessment for?
    Column(
        "day",
        Date,
        nullable=False,
        comment = "The day this score belongs to (one entry per day)."
    ),

    Column(
        "mood",
        Integer,
        nullable=False,
        comment = "Overall mood score for the day (1–7)."
    ),

    Column(
        "created_at",
        DateTime,
        server_default=text
        ("CURRENT_TIMESTAMP"),
        nullable=False,
        comment="When the entry was created (UTC, CURRENT_TIMESTAMP)."
    ),

    UniqueConstraint("day", name="uq_common_mood_log_day"),

    CheckConstraint("mood BETWEEN 1 AND 7", name="ck_common_mood_log_mood_1_7"),

    comment="One overall daily mood score + an optional note."
)

mood_tag_impact = Table(
    "mood_tag_impact",
    metadata,

    Column(
        "id",
        Integer,
        primary_key=True,
        comment="Unique entry identifier."
    ),

    Column(
        "common_mood_log_id",
        Integer,
        ForeignKey("common_mood_log.id", ondelete="CASCADE"),
        nullable=False,
        comment="FK to common_mood_log.id (which day/entry this tag belongs to)."
    ),

    Column(
        "tag",
        Text,
        nullable=False,
        comment="Tag name (e.g., 'sport', 'walk', 'stress')."
    ),

    # -1 / 0 / 1
    Column(
        "impact",
        Integer,
        nullable=False,
        server_default=text("0"),
        comment="Tag impact on mood: -1 (worse), 0 (neutral), 1 (better)."
    ),

    # the same tag does not repeat within the same day
    UniqueConstraint("common_mood_log_id", "tag", name="uq_mood_tag_impact_log_tag"),

    CheckConstraint("impact IN (-1, 0, 1)", name="ck_mood_tag_impact_impact"),
    CheckConstraint("length(tag) > 0", name="ck_mood_tag_impact_tag_not_empty"),

    comment="Day tags and their mood impact (-1/0/1) for a specific common_mood_log entry."
)

mood_log = Table(
    "mood_log",
    metadata,

    Column(
        "id",
        Integer,
        primary_key=True,
        comment = "Unique entry identifier."
    ),

    # What day is the assessment for?
    Column(
        "day",
        Date,
        nullable=False,
        comment = "The day this rating belongs to (one entry per day)."
    ),

    Column(
        "joy",
        Integer,
        nullable=True,
        comment = "Joy (1..4)."
    ),
    Column(
        "interest",
        Integer,
        nullable=True,
        comment = "Interest (1..4)."
    ),
    Column(
        "calm",
        Integer,
        nullable=True,
        comment = "Calm (1..4)."
    ),
    Column(
        "energy",
        Integer,
        nullable=True,
        comment = "Energy (1..4)."
    ),
    Column(
        "anxiety",
        Integer,
        nullable=True,
        comment = "Anxiety (1..4)."
    ),
    Column(
        "sadness",
        Integer,
        nullable=True,
        comment = "Sadness (1..4)."
    ),
    Column(
        "irritation",
        Integer,
        nullable=True,
        comment = "Irritation (1..4)."
    ),
    Column(
        "fatigue",
        Integer,
        nullable=True,
        comment = "Fatigue (1..4)."
    ),
    Column(
        "fear",
        Integer,
        nullable=True,
        comment = "Fear (1..4)."
    ),
    Column(
        "confidence",
        Integer,
        nullable=True,
        comment = "Confidence (1..4)."
    ),
    Column(
        "sleep",
        Integer,
        nullable=True,
        comment = "Sleep / sleep quality (1..4)."
    ),

    # Технічні поля
    Column(
        "created_at",
        DateTime,
        server_default=text("CURRENT_TIMESTAMP"),
        nullable=False,
        comment = "When the entry was created (UTC, CURRENT_TIMESTAMP)."
    ),

    UniqueConstraint("day", name="uq_mood_log_day"),

    # CHECK 1..4 (allow NULL)
    CheckConstraint(
        "joy IS NULL OR (joy BETWEEN 1 AND 4)",
        name="ck_mood_joy_1_4"
    ),
    CheckConstraint(
        "interest IS NULL OR (interest BETWEEN 1 AND 4)",
        name="ck_mood_interest_1_4"
    ),
    CheckConstraint(
        "calm IS NULL OR (calm BETWEEN 1 AND 4)",
        name="ck_mood_calm_1_4"
    ),
    CheckConstraint(
        "energy IS NULL OR (energy BETWEEN 1 AND 4)",
        name="ck_mood_energy_1_4"
    ),
    CheckConstraint(
        "anxiety IS NULL OR (anxiety BETWEEN 1 AND 4)",
        name="ck_mood_anxiety_1_4"
    ),
    CheckConstraint(
        "sadness IS NULL OR (sadness BETWEEN 1 AND 4)",
        name="ck_mood_sadness_1_4"
    ),
    CheckConstraint(
        "irritation IS NULL OR (irritation BETWEEN 1 AND 4)",
        name="ck_mood_irritation_1_4"
    ),
    CheckConstraint(
        "fatigue IS NULL OR (fatigue BETWEEN 1 AND 4)",
        name="ck_mood_fatigue_1_4"
    ),
    CheckConstraint(
        "fear IS NULL OR (fear BETWEEN 1 AND 4)",
        name="ck_mood_fear_1_4"
    ),
    CheckConstraint(
        "confidence IS NULL OR (confidence BETWEEN 1 AND 4)",
        name="ck_mood_confidence_1_4"
    ),
    CheckConstraint(
        "sleep IS NULL OR (sleep BETWEEN 1 AND 4)",
        name="ck_mood_sleep_1_4"
    ),

    comment = "Daily mood/state ratings (scale 1..4, NULL = not filled)."
)
