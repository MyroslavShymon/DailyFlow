from pydantic import BaseModel, Field


class CategoryToActivityDTO(BaseModel):
    category_id: int = Field(ge=1)
    activity_id: int = Field(ge=1)
