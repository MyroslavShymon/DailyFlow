from sqlalchemy import Table, Column, Integer, Text, CheckConstraint, DateTime, UniqueConstraint, text, ForeignKey, Boolean, Index

from .base import metadata

# # Activity — a directory (catalog) of ideas/activities that can then be randomly suggested
activity = Table(
    "activity",
    metadata,

    Column(
        "id",
        Integer,
        primary_key=True,
        comment="Unique activity/idea entry identifier"
    ),
    Column(
        "title",
        Text,
        nullable=False,
        comment="Short activity title (e.g., 'Walk in the park')."
    ),
    Column(
        "description",
        Text,
        nullable=True,
        comment="Detailed description: what to do, scenario, useful details."
    ),

    # ---------- Social context ----------
    Column(
        "social_type",
        Text,
        nullable=True,
        comment="Social format: solo | couple | friends | family | any."
    ),
    Column(
        "people_count_min",
        Integer,
        nullable=True,
        comment="Minimum number of people (including you)."
    ),
    Column(
        "people_count_max",
        Integer,
        nullable=True,
        comment="Maximum number of people (including you)."
    ),
    Column(
        "specific_with",
        Text,
        nullable=True,
        comment="Optional: with whom exactly (e.g., 'partner', 'friend X', 'anyone')."
    ),

    # ---------- Time context ----------
    Column(
        "time_context",
        Text,
        nullable=True,
        comment="When it fits: weekday | weekend | vacation | any."
    ),
    Column(
        "duration_min_minutes",
        Integer,
        nullable=True,
        comment="Minimum duration in minutes (integer)."
    ),
    Column(
        "duration_max_minutes",
        Integer,
        nullable=True,
        comment="Maximum duration in minutes (integer)."
    ),
    Column(
        "time_of_day",
        Text,
        nullable=True,
        comment="Time of day: morning | day | evening | night | flexible."
    ),

    # ---------- Energy / mood model ----------
    Column(
        "energy_required_min",
        Integer,
        nullable=True,
        comment="Min energy required to start (1–5)."
    ),
    Column(
        "energy_required_max",
        Integer,
        nullable=True,
        comment="Max energy required to start (1–5). Used as a range."
    ),
    Column(
        "energy_gain",
        Integer,
        nullable=True,
        comment="After-effect (1–5): 1 drains, 3 neutral, 5 recharges."
    ),
    Column(
        "mood_min",
        Integer,
        nullable=True,
        comment="Min mood/state when this activity fits (1–5)."
    ),
    Column(
        "mood_max",
        Integer,
        nullable=True,
        comment="Max mood/state when this activity fits (1–5)."
    ),

    # ---------- Cost / prep / place ----------
    Column(
        "cost_level",
        Text,
        nullable=True,
        comment="Cost level: free | low(0-500) | medium(500-2000) | high(2000+). Estimate in hryvnias"
    ),
    Column(
        "requires_preparation",
        Boolean,
        nullable=False,
        server_default = text("0"),
        comment="Whether preparation is needed (True/False). If True — see preparation_notes."
    ),
    Column(
        "preparation_notes",
        Text,
        nullable=True,
        comment="What to prepare: items, booking, route, shopping list, etc."
    ),
    Column(
        "location_type",
        Text,
        nullable=True,
        comment="Where it happens: home | city | nature | any."
    ),

    # Lists of values (enum-like)
    CheckConstraint(
        "social_type IS NULL OR social_type IN ('solo','couple','friends','family','any')",
        name="ck_activity_social_type"
    ),
    CheckConstraint(
        "time_context IS NULL OR time_context IN ('weekday','weekend','vacation','any')",
        name="ck_activity_time_context"
    ),
    CheckConstraint(
        "time_of_day IS NULL OR time_of_day IN ('morning','day','evening','night','flexible')",
        name="ck_activity_time_of_day"
    ),
    CheckConstraint(
        "cost_level IS NULL OR cost_level IN ('free','low','medium','high')",
        name="ck_activity_cost_level"
    ),
    CheckConstraint(
        "location_type IS NULL OR location_type IN ('home','city','nature','any')",
        name="ck_activity_location_type"
    ),

    # Numeric ranges
    CheckConstraint(
        "people_count_min IS NULL OR people_count_min >= 1",
        name="ck_activity_people_count_min_ge_1"
    ),
    CheckConstraint(
        "people_count_max IS NULL OR people_count_max >= 1",
        name="ck_activity_people_count_max_ge_1"
    ),
    CheckConstraint(
        "(people_count_min IS NULL OR people_count_max IS NULL) OR people_count_min <= people_count_max",
        name="ck_activity_people_count_min_le_max"
    ),

    CheckConstraint(
        "duration_min_minutes IS NULL OR duration_min_minutes >= 0",
        name="ck_activity_duration_min_ge_0"
    ),
    CheckConstraint(
        "duration_max_minutes IS NULL OR duration_max_minutes >= 0",
        name="ck_activity_duration_max_ge_0"
    ),
    CheckConstraint(
        "(duration_min_minutes IS NULL OR duration_max_minutes IS NULL) OR duration_min_minutes <= duration_max_minutes",
        name="ck_activity_duration_min_le_max"
    ),

    # Scales 1-5
    CheckConstraint(
        "energy_required_min IS NULL OR (energy_required_min BETWEEN 1 AND 5)",
        name="ck_activity_energy_required_min_1_5"
    ),
    CheckConstraint(
        "energy_required_max IS NULL OR (energy_required_max BETWEEN 1 AND 5)",
        name="ck_activity_energy_required_max_1_5"
    ),
    CheckConstraint(
        "(energy_required_min IS NULL OR energy_required_max IS NULL) OR energy_required_min <= energy_required_max",
        name="ck_activity_energy_required_min_le_max"
    ),
    CheckConstraint(
        "energy_gain IS NULL OR (energy_gain BETWEEN 1 AND 5)",
        name="ck_activity_energy_gain_1_5"
    ),
    CheckConstraint(
        "mood_min IS NULL OR (mood_min BETWEEN 1 AND 5)",
        name="ck_activity_mood_min_1_5"
    ),
    CheckConstraint(
        "mood_max IS NULL OR (mood_max BETWEEN 1 AND 5)",
        name="ck_activity_mood_max_1_5"
    ),
    CheckConstraint(
        "(mood_min IS NULL OR mood_max IS NULL) OR mood_min <= mood_max",
        name="ck_activity_mood_min_le_max"
    ),

    # Logical coherence requires_preparation + preparation_notes
    CheckConstraint(
        "requires_preparation IN (0, 1)",
        name="ck_activity_requires_preparation_bool"
    ),
    CheckConstraint(
        "requires_preparation != 0 OR preparation_notes IS NULL OR length(preparation_notes) = 0",
        name="ck_activity_prep_notes_only_when_needed"
    ),

    comment="Activity catalog for the planner generator (weekday/weekend/vacation)."
)

# ActivityUsage — log of actual activity performance (history + grades)
activity_usage = Table(
    "activity_usage",
    metadata,

    Column(
        "id",
        Integer,
        primary_key=True,
        comment="Unique usage entry identifier (one fact of doing an activity)."
    ),
    Column(
        "activity_id",
        Integer,
        ForeignKey("activity.id", ondelete="CASCADE"),
        nullable=False,
        comment="FK to activity.id (which activity was done)."
    ),
    Column(
        "used_at",
        DateTime,
        nullable=False,
        comment="When the activity happened (timestamp)."
    ),

    Column(
        "duration_actual_minutes",
        Integer,
        nullable=True,
        comment="Actual duration in minutes (integer). NULL if unknown."
    ),

    Column(
        "rating_before",
        Integer,
        nullable=True,
        comment="Self-rating before (1–5)."
    ),
    Column(
        "rating_after",
        Integer,
        nullable=True,
        comment="Self-rating after (1–5)."
    ),

    Column(
        "mood_before",
        Integer,
        nullable=True,
        comment="Mood/state before (1–5)."
    ),
    Column(
        "mood_after",
        Integer,
        nullable=True,
        comment="Mood/state after (1–5)."
    ),

    Column(
        "energy_before",
        Integer,
        nullable=True,
        comment="Energy level before (1–5)."
    ),
    Column(
        "energy_after",
        Integer,
        nullable=True,
        comment="Energy level after (1–5)."
    ),

    Column(
        "notes",
        Text,
        nullable=True,
        comment="Optional notes: what worked/didn’t, details, takeaways."
    ),

    CheckConstraint(
        "duration_actual_minutes IS NULL OR duration_actual_minutes >= 0",
        name="ck_activity_usage_duration_actual_minutes_ge_0"
    ),

    # Scales 1–5
    CheckConstraint(
        "rating_before IS NULL OR (rating_before BETWEEN 1 AND 5)",
        name="ck_activity_usage_rating_before_1_5"
    ),
    CheckConstraint(
        "rating_after IS NULL OR (rating_after BETWEEN 1 AND 5)",
        name="ck_activity_usage_rating_after_1_5"
    ),
    CheckConstraint(
        "mood_before IS NULL OR (mood_before BETWEEN 1 AND 5)",
        name="ck_activity_usage_mood_before_1_5"
    ),
    CheckConstraint(
        "mood_after IS NULL OR (mood_after BETWEEN 1 AND 5)",
        name="ck_activity_usage_mood_after_1_5"
    ),
    CheckConstraint(
        "energy_before IS NULL OR (energy_before BETWEEN 1 AND 5)",
        name="ck_activity_usage_energy_before_1_5"
    ),
    CheckConstraint(
        "energy_after IS NULL OR (energy_after BETWEEN 1 AND 5)",
        name="ck_activity_usage_energy_after_1_5"
    ),

    # Minimum consistency: if there is *_after, then there should be used_at (already nullable=False) and preferably *_before
    CheckConstraint(
        "rating_after IS NULL OR rating_before IS NOT NULL",
        name="ck_activity_usage_rating_after_requires_before"
    ),
    CheckConstraint(
        "mood_after IS NULL OR mood_before IS NOT NULL",
        name="ck_activity_usage_mood_after_requires_before"
    ),
    CheckConstraint(
        "energy_after IS NULL OR energy_before IS NOT NULL",
        name="ck_activity_usage_energy_after_requires_before"
    ),

    comment="Activity usage log: when it happened, how long it took, and how state/ratings changed."
)

category = Table(
    "category",
    metadata,

    Column(
        "id",
        Integer,
        primary_key=True,
        comment="Unique category identifier."
    ),
    Column(
        "name",
        Text,
        nullable=False,
        comment="Unique category name (e.g., 'fun', 'rest', 'physical')."
    ),
    Column(
        "description",
        Text,
        nullable=True,
        comment="Optional description: what the category means and what activities belong to it."
    ),

    # Unique name of category
    UniqueConstraint("name", name="uq_category_name"),

    CheckConstraint("length(name) > 0", name="ck_category_name_not_empty"),

    comment="Category dictionary for Activity (many-to-many)."
)

category_activity = Table(
    "category_activity",
    metadata,

    Column(
        "category_id",
        Integer,
        ForeignKey("category.id", ondelete="CASCADE"),
        primary_key=True,
        nullable=False,
        comment="FK to category.id. The category linked to an activity."
    ),
    Column(
        "activity_id",
        Integer,
        ForeignKey("activity.id", ondelete="CASCADE"),
        primary_key=True,
        nullable=False,
        comment="FK to activity.id. The activity assigned to a category."
    ),

    Index("ix_category_activity_activity_id", "activity_id"),

    comment="Many-to-many link table between Activity and Category."
)
