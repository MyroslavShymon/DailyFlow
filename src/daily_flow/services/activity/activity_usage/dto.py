from datetime import datetime
from typing import Annotated

from pydantic import BaseModel, Field

Score1to5 = Annotated[int, Field(ge=1, le=5)]
NonNegInt = Annotated[int, Field(ge=0)]


class UpsertActivityUsageDTO(BaseModel):
    usage_id: int | None = Field(default=None, ge=1)

    activity_id: int = Field(ge=1)
    used_at: datetime

    duration_actual_minutes: NonNegInt | None = None

    rating_before: Score1to5 | None = None
    rating_after: Score1to5 | None = None

    mood_before: Score1to5 | None = None
    mood_after: Score1to5 | None = None

    energy_before: Score1to5 | None = None
    energy_after: Score1to5 | None = None

    notes: Annotated[str | None, Field(min_length=1)] = None


class ActivityUsagePeriodDTO(BaseModel):
    date_from: datetime
    date_to: datetime
