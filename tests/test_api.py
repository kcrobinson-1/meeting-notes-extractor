from _pytest.monkeypatch import MonkeyPatch
from fastapi.testclient import TestClient

import app.main as main_module
from app.main import app
from app.schemas import ExtractResponse

client = TestClient(app)


def test_health_check_returns_ok() -> None:
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_extract_returns_structured_response() -> None:
    response = client.post(
        "/extract",
        json={
            "meeting_title": "Platform sync",
            "meeting_date": "2026-03-27",
            "notes_text": (
                "Alice said the migration slips by 2 weeks. "
                "Bob owns the rollback doc by Friday. "
                "Do we need to notify partners?"
            ),
        },
    )

    assert response.status_code == 200
    assert response.json() == {
        "summary": (
            'The meeting "Platform sync" covered the migration slips by 2 weeks, '
            "Bob owning the rollback doc, an open question about do we need to "
            "notify partners."
        ),
        "decisions": ["The migration slips by 2 weeks"],
        "action_items": [
            {
                "task": "the rollback doc",
                "owner": "Bob",
                "due_date": "2026-04-03",
            }
        ],
        "open_questions": ["Do we need to notify partners?"],
        "ambiguities": [],
    }


def test_extract_uses_ai_strategy_when_configured(
    monkeypatch: MonkeyPatch,
) -> None:
    expected_response = ExtractResponse(
        summary="AI summary",
        decisions=[],
        action_items=[],
        open_questions=[],
        ambiguities=[],
    )

    def fake_extract_meeting_notes(request: object, strategy: str) -> ExtractResponse:
        assert strategy == "ai"
        return expected_response

    monkeypatch.setenv("EXTRACTOR_STRATEGY", "ai")
    monkeypatch.setattr(
        main_module, "extract_meeting_notes", fake_extract_meeting_notes
    )

    response = client.post("/extract", json={"notes_text": "Alice said hello."})

    assert response.status_code == 200
    assert response.json() == expected_response.model_dump(mode="json")


def test_extract_rejects_invalid_configured_strategy(
    monkeypatch: MonkeyPatch,
) -> None:
    invalid_client = TestClient(app, raise_server_exceptions=False)

    monkeypatch.setenv("EXTRACTOR_STRATEGY", "surprise")

    response = invalid_client.post("/extract", json={"notes_text": "Alice said hello."})

    assert response.status_code == 500
    assert response.json() == {
        "detail": "EXTRACTOR_STRATEGY must be one of: deterministic, ai."
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
