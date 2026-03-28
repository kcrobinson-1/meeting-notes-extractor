from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_check_returns_ok() -> None:
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_extract_returns_dummy_response() -> None:
    response = client.post(
        "/extract",
        json={
            "meeting_title": "Platform sync",
            "meeting_date": "2026-03-27",
            "notes_text": "Alice said the migration slips by 2 weeks.",
        },
    )

    assert response.status_code == 200
    assert response.json() == {
        "summary": (
            'Dummy summary for "Platform sync" based on the provided meeting notes.'
        ),
        "decisions": ["Dummy decision: proceed with the next planned step."],
        "action_items": [
            {
                "task": "Dummy action item",
                "owner": "Bob",
                "due_date": "2026-04-03",
            }
        ],
        "open_questions": ["Dummy open question: is any follow-up needed?"],
        "ambiguities": [
            (
                "Dummy ambiguity: dates and owners may be inferred in a real "
                "implementation."
            ),
            "Meeting date was provided as 2026-03-27.",
        ],
    }


def test_extract_requires_notes_text() -> None:
    response = client.post("/extract", json={})

    assert response.status_code == 422


def test_extract_rejects_empty_notes_text() -> None:
    response = client.post(
        "/extract",
        json={"notes_text": ""},
    )

    assert response.status_code == 422


def test_extract_rejects_blank_notes_text() -> None:
    response = client.post(
        "/extract",
        json={"notes_text": "   "},
    )

    assert response.status_code == 422


def test_extract_rejects_extra_request_fields() -> None:
    response = client.post(
        "/extract",
        json={
            "notes_text": "Alice said the migration slips by 2 weeks.",
            "unexpected_field": "surprise",
        },
    )

    assert response.status_code == 422


def test_extract_rejects_invalid_meeting_date() -> None:
    response = client.post(
        "/extract",
        json={
            "meeting_date": "not-a-date",
            "notes_text": "Alice said the migration slips by 2 weeks.",
        },
    )

    assert response.status_code == 422


def test_extract_rejects_malformed_json() -> None:
    response = client.post(
        "/extract",
        content=b'{"notes_text": "Alice said the migration slips by 2 weeks."',
        headers={"content-type": "application/json"},
    )

    assert response.status_code == 422


def test_openapi_describes_extract_contract() -> None:
    response = client.get("/openapi.json")

    assert response.status_code == 200

    openapi = response.json()
    extract_operation = openapi["paths"]["/extract"]["post"]

    assert (
        extract_operation["requestBody"]["content"]["application/json"]["schema"][
            "$ref"
        ]
        == "#/components/schemas/ExtractRequest"
    )
    assert (
        extract_operation["responses"]["200"]["content"]["application/json"]["schema"][
            "$ref"
        ]
        == "#/components/schemas/ExtractResponse"
    )
