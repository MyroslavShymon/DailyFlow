from sqlalchemy import Table, Column, Integer, Date, Text, CheckConstraint, UniqueConstraint

from .base import metadata

learning_log = Table(
    "learning_log",
    metadata,

    Column(
        "id",
        Integer,
        primary_key=True,
        comment="Unique learning log entry."
    ),
    Column(
        "day",
        Date,
        nullable=False,
        comment="Day the learning happened."
    ),
    Column(
        "description",
        Text,
        nullable=True,
        comment="What was learned or studied."
    ),
    Column(
        "time_spent_minutes",
        Integer,
        nullable=True,
        comment="Time spent learning (minutes)."
    ),
    Column(
        "effectiveness",
        Integer,
        nullable=True,
        comment="How effective the learning felt (1–5)."
    ),
    Column(
        "difficulty",
        Integer,
        nullable=True,
        comment="How hard it felt (1–5)."
    ),

    UniqueConstraint("day", name="uq_learning_log_day"),
    CheckConstraint("effectiveness IS NULL OR effectiveness BETWEEN 1 AND 5",
                    name="ck_learning_log_effectiveness_1_5"),
    CheckConstraint(
        "difficulty IS NULL OR difficulty BETWEEN 1 AND 5",
        name="ck_learning_log_difficulty_1_5"
    ),

    comment="Daily learning activity and self-evaluation."
)

work_log = Table(
    "work_log",
    metadata,

    Column(
        "id",
        Integer,
        primary_key=True,
        comment="Unique work log entry."
    ),
    Column(
        "day",
        Date,
        nullable=False,
        comment="Day the work log refers to."
    ),
    Column(
        "time_spent_minutes",
        Integer,
        nullable=True,
        comment="Time spent working (minutes)."
    ),
    Column(
        "what_done",
        Text,
        nullable=True,
        comment="What was done that day."
    ),
    Column(
        "interesting",
        Text,
        nullable=True,
        comment="What was interesting."
    ),
    Column(
        "not_interesting",
        Text,
        nullable=True,
        comment="What was boring or unpleasant."
    ),
    Column(
        "effectiveness",
        Integer,
        nullable=True,
        comment="Self-rated effectiveness (1–5)."
    ),
    Column(
        "focus_level",
        Integer,
        nullable=True,
        comment="Focus level during work (1–5)."
    ),
    Column(
        "difficulty",
        Integer,
        nullable=True,
        comment="How hard it felt (1–5)."
    ),
    Column(
        "topics",
        Text,
        nullable=True,
        comment="Topics covered during work (comma-separated, e.g. 'pandas,ml,math')."
    ),

    UniqueConstraint("day", name="uq_work_log_day"),

    CheckConstraint("effectiveness IS NULL OR effectiveness BETWEEN 1 AND 5",
                    name="ck_work_log_effectiveness_1_5"),
    CheckConstraint(
        "difficulty IS NULL OR difficulty BETWEEN 1 AND 5",
        name="ck_work_log_difficulty_1_5"
    ),
    CheckConstraint(
        "topics IS NULL OR length(topics) <= 200",
        name="ck_work_log_topics_len_200"
    ),
    CheckConstraint(
        "topics IS NULL OR length(trim(topics)) > 0",
        name="ck_work_log_topics_not_blank"
    ),
    CheckConstraint(
        "focus_level IS NULL OR focus_level BETWEEN 1 AND 5",
        name="ck_work_log_focus_level_1_5"
    ),

    comment="Daily work reflection and self-evaluation."
)
