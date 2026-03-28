import os
from datetime import date
from typing import Any, Protocol, cast

from dotenv import load_dotenv
from openai import APIError, OpenAI, RateLimitError

from app.schemas import ExtractRequest, ExtractResponse

DEFAULT_OPENAI_MODEL = "gpt-5-mini"

SYSTEM_PROMPT = """
You extract structured data from meeting notes.

Return data that matches the provided schema exactly.
Do not invent facts.
If something is unclear or inferred, include it in ambiguities instead of guessing.
Summaries should be concise.
Action items should include owner and due_date only when the notes support them.
If meeting_date is provided, resolve relative dates against that date.
If meeting_date is missing, resolve relative dates against today's date.
For example, "next Wednesday" should resolve to a due date on the Wednesday following 
the meeting_date or the Wednesday after today if no meeting_date is supplied.
If you still cannot resolve a relative date confidently, leave due_date null and
add an ambiguity explaining why.
Do not invent decisions; only include them when the notes clearly state one.
""".strip()

load_dotenv()


class OpenAIConfigurationError(RuntimeError):
    """Raised when required OpenAI configuration is missing."""


class OpenAIResponseFormatError(RuntimeError):
    """Raised when the OpenAI response cannot be parsed into the schema."""


class OpenAIRequestError(RuntimeError):
    """Raised when the OpenAI request fails before a parsed response is returned."""


class ResponsesParserClient(Protocol):
    responses: Any


def parse_meeting_notes_with_openai(
    request: ExtractRequest, client: ResponsesParserClient | None = None
) -> ExtractResponse:
    openai_client = client or create_openai_client()
    try:
        response = openai_client.responses.parse(
            model=get_openai_model(),
            input=cast(Any, build_openai_input(request)),
            text_format=ExtractResponse,
        )
    except RateLimitError as exc:
        raise OpenAIRequestError(
            "OpenAI request failed because the API project has no available quota. "
            "Check billing and usage for the configured API key."
        ) from exc
    except APIError as exc:
        raise OpenAIRequestError(
            f"OpenAI request failed: {exc.__class__.__name__}."
        ) from exc

    parsed_response = getattr(response, "output_parsed", None)
    if isinstance(parsed_response, ExtractResponse):
        return parsed_response

    raise OpenAIResponseFormatError(
        "OpenAI returned a response that could not be parsed into ExtractResponse."
    )


def create_openai_client() -> OpenAI:
    return OpenAI(api_key=get_openai_api_key())


def get_openai_api_key() -> str:
    api_key = os.getenv("OPENAI_API_KEY")
    if api_key:
        return api_key

    raise OpenAIConfigurationError(
        "OPENAI_API_KEY must be set to use the AI extractor."
    )


def get_openai_model() -> str:
    return os.getenv("OPENAI_MODEL", DEFAULT_OPENAI_MODEL)


def build_openai_input(request: ExtractRequest) -> list[dict[str, Any]]:
    reference_date = request.meeting_date or date.today()
    request_lines = ["Meeting notes:"]

    if request.meeting_title:
        request_lines.append(f"Meeting title: {request.meeting_title}")

    if request.meeting_date:
        request_lines.append(f"Meeting date: {request.meeting_date.isoformat()}")
    else:
        request_lines.append(
            f"Reference date for relative dates: {reference_date.isoformat()}"
        )

    request_lines.append(f"Notes text: {request.notes_text}")

    return [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": "\n".join(request_lines)},
    ]
