from typing import Annotated

from pydantic import BaseModel, Field


class UpsertCategoryDTO(BaseModel):
    name: Annotated[str, Field(min_length=1)]
    description: Annotated[str | None, Field(min_length=1)] = None
