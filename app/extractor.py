from typing import Literal

from app.extractors import (
    AIMeetingNotesExtractor,
    DeterministicMeetingNotesExtractor,
    InvalidExtractorStrategyError,
    MeetingNotesExtractor,
    OpenAIConfigurationError,
    OpenAIRequestError,
    OpenAIResponseFormatError,
)
from app.schemas import ExtractRequest, ExtractResponse

ExtractorStrategy = Literal["deterministic", "ai"]

_EXTRACTORS: dict[ExtractorStrategy, MeetingNotesExtractor] = {
    "deterministic": DeterministicMeetingNotesExtractor(),
    "ai": AIMeetingNotesExtractor(),
}


def extract_meeting_notes(
    request: ExtractRequest, strategy: ExtractorStrategy = "deterministic"
) -> ExtractResponse:
    extractor = get_extractor(strategy)
    return extractor.extract(request)


def get_extractor(strategy: ExtractorStrategy) -> MeetingNotesExtractor:
    return _EXTRACTORS[strategy]


__all__ = [
    "AIMeetingNotesExtractor",
    "DeterministicMeetingNotesExtractor",
    "ExtractorStrategy",
    "InvalidExtractorStrategyError",
    "MeetingNotesExtractor",
    "OpenAIConfigurationError",
    "OpenAIRequestError",
    "OpenAIResponseFormatError",
    "extract_meeting_notes",
    "get_extractor",
]
