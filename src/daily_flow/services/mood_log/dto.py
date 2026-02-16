from datetime import date
from typing import Annotated

from pydantic import BaseModel, Field

Score1to4 = Annotated[int, Field(ge=1, le=4)]

class UpsertMoodLogDTO(BaseModel):
    day: date
    joy: Score1to4 | None = None
    interest: Score1to4 | None = None
    calm: Score1to4 | None = None
    energy: Score1to4 | None = None
    anxiety: Score1to4 | None = None
    sadness: Score1to4 | None = None
    irritation: Score1to4 | None = None
    fatigue: Score1to4 | None = None
    fear: Score1to4 | None = None
    confidence: Score1to4 | None = None
    sleep: Score1to4 | None = None