from datetime import date
from typing import Annotated, Literal

from pydantic import BaseModel, Field

class UpsertCommonMoodLogDTO(BaseModel):
    day: date
    mood: Annotated[int | None, Field(ge=1, le=7)] = None
    note: Annotated[str | None, Field(min_length=1)] = None

class UpsertTagImpactDTO(BaseModel):
    day: date
    tag: Annotated[str, Field(min_length=1)]
    impact: Literal[-1, 0, 1]