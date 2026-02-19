from typing import Annotated, Literal

from pydantic import BaseModel, Field

Score1to5 = Annotated[int, Field(ge=1, le=5)]
NonNegInt = Annotated[int, Field(ge=0)]
PeopleCount = Annotated[int, Field(ge=1)]


class UpsertActivityDTO(BaseModel):
    title: Annotated[str, Field(min_length=1)]

    description: Annotated[str | None, Field(min_length=1)] = None

    social_type: Literal["solo", "couple", "friends", "family", "any"] | None = None
    people_count_min: PeopleCount | None = None
    people_count_max: PeopleCount | None = None
    specific_with: Annotated[str | None, Field(min_length=1)] = None

    time_context: Literal["weekday", "weekend", "vacation", "any"] | None = None
    duration_min_minutes: NonNegInt | None = None
    duration_max_minutes: NonNegInt | None = None
    time_of_day: Literal["morning", "day", "evening", "night", "flexible"] | None = None

    energy_required_min: Score1to5 | None = None
    energy_required_max: Score1to5 | None = None
    energy_gain: Score1to5 | None = None
    mood_min: Score1to5 | None = None
    mood_max: Score1to5 | None = None

    cost_level: Literal["free", "low", "medium", "high"] | None = None
    requires_preparation: bool | None = None
    preparation_notes: Annotated[str | None, Field(min_length=1)] = None
    location_type: Literal["home", "city", "nature", "any"] | None = None
