from datetime import date
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field, StringConstraints

NonEmptyStr = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)]


class ExtractRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    meeting_title: NonEmptyStr | None = None
    meeting_date: date | None = None
    notes_text: NonEmptyStr = Field()


class ActionItem(BaseModel):
    task: NonEmptyStr
    owner: NonEmptyStr | None = None
    due_date: date | None = None


class ExtractResponse(BaseModel):
    summary: NonEmptyStr
    decisions: list[NonEmptyStr]
    action_items: list[ActionItem]
    open_questions: list[NonEmptyStr]
    ambiguities: list[NonEmptyStr]
