from datetime import date

import pytest
from pydantic import ValidationError

from app.schemas import ActionItem, ExtractRequest


def test_extract_request_parses_iso_meeting_date() -> None:
    request = ExtractRequest.model_validate(
        {
            "meeting_title": "Platform sync",
            "meeting_date": "2026-03-27",
            "notes_text": "Alice said the migration slips by 2 weeks.",
        }
    )

    assert request.meeting_date == date(2026, 3, 27)


def test_extract_request_rejects_blank_meeting_title() -> None:
    with pytest.raises(ValidationError):
        ExtractRequest(
            meeting_title="   ",
            notes_text="Alice said the migration slips by 2 weeks.",
        )


def test_extract_request_rejects_extra_fields() -> None:
    with pytest.raises(ValidationError):
        ExtractRequest.model_validate(
            {
                "notes_text": "Alice said the migration slips by 2 weeks.",
                "unexpected_field": "surprise",
            }
        )


def test_action_item_serializes_due_date_as_iso_string() -> None:
    action_item = ActionItem(
        task="Write rollback document",
        owner="Bob",
        due_date=date(2026, 4, 3),
    )

    assert action_item.model_dump(mode="json") == {
        "task": "Write rollback document",
        "owner": "Bob",
        "due_date": "2026-04-03",
    }
