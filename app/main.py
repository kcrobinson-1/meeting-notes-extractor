from fastapi import FastAPI

from app.extractor import extract_meeting_notes
from app.schemas import ExtractRequest, ExtractResponse

app = FastAPI()


@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/extract", response_model=ExtractResponse)
def extract_notes(request: ExtractRequest) -> ExtractResponse:
    return extract_meeting_notes(request)
