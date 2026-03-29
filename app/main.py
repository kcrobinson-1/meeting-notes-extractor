from fastapi import FastAPI, HTTPException

from app.extractor import extract_meeting_notes
from app.schemas import ExtractRequest, ExtractResponse
from app.settings import InvalidExtractorStrategyError, get_extractor_strategy

app = FastAPI()


@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/extract", response_model=ExtractResponse)
def extract_notes(request: ExtractRequest) -> ExtractResponse:
    try:
        strategy = get_extractor_strategy()
    except InvalidExtractorStrategyError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    return extract_meeting_notes(request, strategy=strategy)
