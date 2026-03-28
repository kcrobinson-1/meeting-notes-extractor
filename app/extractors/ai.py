from collections.abc import Callable

from app.extractors.base import MeetingNotesExtractor
from app.openai_client import parse_meeting_notes_with_openai
from app.schemas import ExtractRequest, ExtractResponse


class AIMeetingNotesExtractor(MeetingNotesExtractor):
    def __init__(
        self,
        parser: Callable[[ExtractRequest], ExtractResponse] = (
            parse_meeting_notes_with_openai
        ),
    ) -> None:
        self._parser = parser

    def extract(self, request: ExtractRequest) -> ExtractResponse:
        return self._parser(request)
