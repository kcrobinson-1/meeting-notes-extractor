from datetime import date

from app.extractor import extract_meeting_notes
from app.schemas import ExtractRequest


def test_extract_meeting_notes_uses_meeting_metadata() -> None:
    response = extract_meeting_notes(
        ExtractRequest(
            meeting_title="Platform sync",
            meeting_date=date(2026, 3, 27),
            notes_text="Alice said the migration slips by 2 weeks.",
        )
    )

    assert response.summary == (
        'Dummy summary for "Platform sync" based on the provided meeting notes.'
    )
    assert response.action_items[0].due_date == date(2026, 4, 3)
    assert response.ambiguities == [
        "Dummy ambiguity: dates and owners may be inferred in a real implementation.",
        "Meeting date was provided as 2026-03-27.",
    ]


def test_extract_meeting_notes_without_metadata_uses_base_dummy_summary() -> None:
    response = extract_meeting_notes(
        ExtractRequest(notes_text="Alice said the migration slips by 2 weeks.")
    )

    assert response.summary == "Dummy summary for the provided meeting notes."
    assert response.ambiguities == [
        "Dummy ambiguity: dates and owners may be inferred in a real implementation."
    ]
