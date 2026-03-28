from abc import ABC, abstractmethod

from app.schemas import ExtractRequest, ExtractResponse


class MeetingNotesExtractor(ABC):
    @abstractmethod
    def extract(self, request: ExtractRequest) -> ExtractResponse:
        """Extract structured meeting data from a request."""
