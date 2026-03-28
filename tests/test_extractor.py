from datetime import date

import pytest

from app.extractor import extract_meeting_notes, get_extractor
from app.extractors.ai import AIExtractorNotImplementedError, AIMeetingNotesExtractor
from app.extractors.base import MeetingNotesExtractor
from app.extractors.deterministic import DeterministicMeetingNotesExtractor
from app.schemas import ExtractRequest


def test_deterministic_extractor_uses_meeting_metadata() -> None:
    response = DeterministicMeetingNotesExtractor().extract(
        ExtractRequest(
            meeting_title="Platform sync",
            meeting_date=date(2026, 3, 27),
            notes_text=(
                "Alice said the migration slips by 2 weeks. "
                "Bob owns the rollback doc by Friday. "
                "Do we need to notify partners?"
            ),
        )
    )

    assert response.summary == (
        'The meeting "Platform sync" covered the migration slips by 2 weeks, '
        "Bob owning the rollback doc, an open question about do we need to "
        "notify partners."
    )
    assert response.decisions == ["The migration slips by 2 weeks"]
    assert [action_item.model_dump() for action_item in response.action_items] == [
        {
            "task": "the rollback doc",
            "owner": "Bob",
            "due_date": date(2026, 4, 3),
        }
    ]
    assert response.open_questions == ["Do we need to notify partners?"]
    assert response.ambiguities == []


def test_get_extractor_returns_implementation_instances() -> None:
    deterministic_extractor = get_extractor("deterministic")
    ai_extractor = get_extractor("ai")

    assert isinstance(deterministic_extractor, MeetingNotesExtractor)
    assert isinstance(deterministic_extractor, DeterministicMeetingNotesExtractor)
    assert isinstance(ai_extractor, MeetingNotesExtractor)
    assert isinstance(ai_extractor, AIMeetingNotesExtractor)


def test_default_extractor_matches_deterministic_strategy() -> None:
    request = ExtractRequest(notes_text="Alice said the migration slips by 2 weeks.")

    default_response = extract_meeting_notes(request)
    deterministic_response = get_extractor("deterministic").extract(request)

    assert default_response == deterministic_response


def test_ai_extractor_stub_raises_not_implemented() -> None:
    with pytest.raises(AIExtractorNotImplementedError):
        AIMeetingNotesExtractor().extract(
            ExtractRequest(notes_text="Alice said the migration slips by 2 weeks."),
        )


def test_extract_meeting_notes_ai_strategy_routes_to_ai_extractor() -> None:
    with pytest.raises(AIExtractorNotImplementedError):
        extract_meeting_notes(
            ExtractRequest(notes_text="Alice said the migration slips by 2 weeks."),
            strategy="ai",
        )


def test_deterministic_extractor_records_due_date_ambiguity_without_meeting_date() -> (
    None
):
    response = DeterministicMeetingNotesExtractor().extract(
        ExtractRequest(notes_text="Bob owns the rollback doc by Friday.")
    )

    assert response.summary == (
        "The meeting notes covered Bob owning the rollback doc."
    )
    assert [action_item.model_dump() for action_item in response.action_items] == [
        {
            "task": "the rollback doc",
            "owner": "Bob",
            "due_date": None,
        }
    ]
    assert response.ambiguities == [
        (
            'Due date "Friday" for task "the rollback doc" could not be '
            "resolved without a meeting_date."
        )
    ]


def test_deterministic_extractor_without_supported_patterns_returns_ambiguity() -> None:
    response = DeterministicMeetingNotesExtractor().extract(
        ExtractRequest(notes_text="We discussed several topics and need more detail.")
    )

    assert response.summary == (
        "The meeting notes covered follow-up items that still need clarification."
    )
    assert response.decisions == []
    assert response.action_items == []
    assert response.open_questions == []
    assert response.ambiguities == [
        "No structured items could be confidently extracted."
    ]
