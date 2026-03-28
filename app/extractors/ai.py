from app.extractors.base import MeetingNotesExtractor
from app.schemas import ExtractRequest, ExtractResponse


class AIExtractorNotImplementedError(NotImplementedError):
    """Raised when the AI extraction strategy has not been wired yet."""


class AIMeetingNotesExtractor(MeetingNotesExtractor):
    def extract(self, request: ExtractRequest) -> ExtractResponse:
        raise AIExtractorNotImplementedError(
            "The AI extractor is not wired yet. Add model integration here and keep "
            "the ExtractResponse contract unchanged."
        )
