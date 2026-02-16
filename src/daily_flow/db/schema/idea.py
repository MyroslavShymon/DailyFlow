from sqlalchemy import Table, Column, Integer, Text, CheckConstraint, DateTime, UniqueConstraint, ForeignKey, text

from .base import metadata

sphere = Table(
    "sphere",
    metadata,

    Column(
        "id",
        Integer,
        primary_key=True,
        comment="Unique sphere identifier."
    ),
    Column(
        "name",
        Text,
        nullable=False,
        comment="Sphere name (e.g. 'career', 'startup', 'learning')."
    ),
    Column(
        "description",
        Text,
        nullable=True,
        comment="Optional description of what belongs to this sphere."
    ),

    UniqueConstraint("name", name="uq_sphere_name"),
    CheckConstraint("length(trim(name)) > 0", name="ck_sphere_name_not_blank"),

    comment="Spheres are high-level life areas used to group ideas."
)

idea = Table(
    "idea",
    metadata,

    Column(
        "id",
        Integer,
        primary_key=True,
        comment="Unique idea identifier."
    ),
    Column(
        "title",
        Text,
        nullable=False,
        comment="Short idea title."
    ),
    Column(
        "description",
        Text,
        nullable=True,
        comment="Explanation or details of the idea."
    ),
    Column(
        "intent",
        Text,
        nullable=True,
        comment="Idea intent: problem | solution | hypothesis | question | insight | todo."
    ),
    Column(
        "created_at",
        DateTime,
        server_default=text("CURRENT_TIMESTAMP"),
        nullable=False,
        comment="When the idea was created."
    ),

    UniqueConstraint("title", name="uq_idea_title"),

    CheckConstraint("length(trim(title)) > 0", name="ck_idea_title_not_blank"),
    CheckConstraint(
        "intent IS NULL OR intent IN ('problem','solution','hypothesis','question','insight','todo')",
        name="ck_idea_intent"
    ),

    comment="General ideas with an optional intent label."
)

idea_sphere = Table(
    "idea_sphere",
    metadata,

    Column(
        "idea_id",
        Integer,
        ForeignKey("idea.id", ondelete="CASCADE"),
        primary_key=True,
        nullable=False,
        comment="FK to idea.id."
    ),
    Column(
        "sphere_id",
        Integer,
        ForeignKey("sphere.id", ondelete="CASCADE"),
        primary_key=True,
        nullable=False,
        comment="FK to sphere.id."
    ),

    comment="Many-to-many link between ideas and spheres."
)

