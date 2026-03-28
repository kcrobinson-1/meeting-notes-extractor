from typing import Literal

from app.extractors import (
    AIExtractorNotImplementedError,
    AIMeetingNotesExtractor,
    DeterministicMeetingNotesExtractor,
    MeetingNotesExtractor,
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
    "AIExtractorNotImplementedError",
    "AIMeetingNotesExtractor",
    "DeterministicMeetingNotesExtractor",
    "ExtractorStrategy",
    "MeetingNotesExtractor",
    "extract_meeting_notes",
    "get_extractor",
]
