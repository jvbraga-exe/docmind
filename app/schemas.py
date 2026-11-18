from uuid import UUID

from pydantic import BaseModel, Field


class Question(BaseModel):
    question: str = Field(min_length=4, max_length=500)
    document_id: UUID | None = None
