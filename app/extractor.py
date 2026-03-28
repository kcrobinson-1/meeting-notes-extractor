from datetime import date

from app.schemas import ActionItem, ExtractRequest, ExtractResponse


def extract_meeting_notes(request: ExtractRequest) -> ExtractResponse:
    summary = "Dummy summary for the provided meeting notes."
    ambiguities = [
        "Dummy ambiguity: dates and owners may be inferred in a real implementation."
    ]

    if request.meeting_title:
        summary = (
            f'Dummy summary for "{request.meeting_title}" based on the provided '
            "meeting notes."
        )

    if request.meeting_date:
        ambiguities.append(
            f"Meeting date was provided as {request.meeting_date.isoformat()}."
        )

    return ExtractResponse(
        summary=summary,
        decisions=["Dummy decision: proceed with the next planned step."],
        action_items=[
            ActionItem(
                task="Dummy action item",
                owner="Bob",
                due_date=date(2026, 4, 3),
            )
        ],
        open_questions=["Dummy open question: is any follow-up needed?"],
        ambiguities=ambiguities,
    )
