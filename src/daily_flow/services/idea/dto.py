from typing import Annotated

from pydantic import BaseModel, Field

from daily_flow.db.repositories.idea_repo import IdeaIntent

class UpsertSphereDTO(BaseModel):
    name: Annotated[str, Field(min_length=1)]
    description: Annotated[str | None, Field(min_length=1)] = None

class UpsertIdeaDTO(BaseModel):
    title: Annotated[str, Field(min_length=1)]
    description: Annotated[str | None, Field(min_length=1)] = None
    intent: IdeaIntent | None = None

class SphereToIdeaDTO(BaseModel):
    sphere_id: int
    idea_id: int