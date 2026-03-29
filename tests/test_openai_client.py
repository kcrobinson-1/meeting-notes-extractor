from datetime import date
from types import SimpleNamespace

import pytest
from openai import APIError, RateLimitError

from app.openai_client import (
    OpenAIRequestError,
    OpenAIResponseFormatError,
    build_openai_input,
    get_openai_api_key,
    get_openai_model,
    parse_meeting_notes_with_openai,
)
from app.schemas import ExtractRequest, ExtractResponse
from app.settings import DEFAULT_OPENAI_MODEL, OpenAIConfigurationError


class FakeResponsesAPI:
    def __init__(self, parsed_response: object) -> None:
        self._parsed_response = parsed_response
        self.last_kwargs: dict[str, object] | None = None

    def parse(self, **kwargs: object) -> SimpleNamespace:
        self.last_kwargs = kwargs
        return SimpleNamespace(output_parsed=self._parsed_response)


class FakeOpenAIClient:
    def __init__(self, parsed_response: object) -> None:
        self.responses = FakeResponsesAPI(parsed_response)


class FakeErrorResponsesAPI:
    def __init__(self, error: Exception) -> None:
        self._error = error

    def parse(self, **kwargs: object) -> SimpleNamespace:
        raise self._error


class FakeErrorOpenAIClient:
    def __init__(self, error: Exception) -> None:
        self.responses = FakeErrorResponsesAPI(error)


class FakeRateLimitError(RateLimitError):
    def __init__(self) -> None:
        Exception.__init__(self, "insufficient quota")


class FakeAPIError(APIError):
    def __init__(self) -> None:
        Exception.__init__(self, "upstream failure")


def test_parse_meeting_notes_with_openai_returns_parsed_response() -> None:
    expected_response = ExtractResponse(
        summary="AI summary",
        decisions=["Delay the migration"],
        action_items=[],
        open_questions=[],
        ambiguities=[],
    )
    client = FakeOpenAIClient(expected_response)

    response = parse_meeting_notes_with_openai(
        ExtractRequest(
            meeting_title="Platform sync",
            notes_text="Alice said the migration slips by 2 weeks.",
        ),
        client=client,
    )

    assert response == expected_response
    assert client.responses.last_kwargs is not None
    assert client.responses.last_kwargs["model"] == DEFAULT_OPENAI_MODEL
    assert client.responses.last_kwargs["text_format"] is ExtractResponse


def test_parse_meeting_notes_with_openai_rejects_unparsed_output() -> None:
    client = FakeOpenAIClient(parsed_response=None)

    with pytest.raises(OpenAIResponseFormatError):
        parse_meeting_notes_with_openai(
            ExtractRequest(notes_text="Alice said the migration slips by 2 weeks."),
            client=client,
        )


def test_parse_meeting_notes_with_openai_wraps_quota_errors() -> None:
    client = FakeErrorOpenAIClient(FakeRateLimitError())

    with pytest.raises(OpenAIRequestError, match="no available quota"):
        parse_meeting_notes_with_openai(
            ExtractRequest(notes_text="Alice said the migration slips by 2 weeks."),
            client=client,
        )


def test_parse_meeting_notes_with_openai_wraps_api_errors() -> None:
    client = FakeErrorOpenAIClient(FakeAPIError())

    with pytest.raises(OpenAIRequestError, match="APIError"):
        parse_meeting_notes_with_openai(
            ExtractRequest(notes_text="Alice said the migration slips by 2 weeks."),
            client=client,
        )


def test_get_openai_api_key_requires_env_var(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)

    with pytest.raises(OpenAIConfigurationError):
        get_openai_api_key()


def test_get_openai_model_uses_env_override(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("OPENAI_MODEL", "gpt-4.1-mini")

    assert get_openai_model() == "gpt-4.1-mini"


def test_build_openai_input_includes_request_metadata() -> None:
    openai_input = build_openai_input(
        ExtractRequest(
            meeting_title="Platform sync",
            meeting_date=date(2026, 3, 27),
            notes_text="Alice said the migration slips by 2 weeks.",
        )
    )

    assert openai_input[0]["role"] == "system"
    assert openai_input[1]["role"] == "user"
    assert "Meeting title: Platform sync" in openai_input[1]["content"]
    assert "Meeting date: 2026-03-27" in openai_input[1]["content"]
    assert (
        "Notes text: Alice said the migration slips by 2 weeks."
        in openai_input[1]["content"]
    )


def test_build_openai_input_uses_today_when_meeting_date_is_missing(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    class FixedDateFactory:
        @staticmethod
        def today() -> date:
            return date(2026, 3, 24)

    monkeypatch.setattr("app.openai_client.date", FixedDateFactory)

    openai_input = build_openai_input(
        ExtractRequest(notes_text="Bob owns the rollback doc by Friday.")
    )

    assert "Reference date for relative dates: 2026-03-24" in openai_input[1]["content"]
