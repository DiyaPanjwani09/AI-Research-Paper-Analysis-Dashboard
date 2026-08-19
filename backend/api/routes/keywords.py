from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import List, Dict

from services.keyword_service import KeywordExtractionService

router = APIRouter()

_keyword_service: KeywordExtractionService = None


def _get_service() -> KeywordExtractionService:
    global _keyword_service
    if _keyword_service is None:
        _keyword_service = KeywordExtractionService()
    return _keyword_service


class KeywordRequest(BaseModel):
    paper_text: str = Field(..., min_length=50)
    top_k: int = Field(default=20, ge=1, le=100)


class KeywordResponse(BaseModel):
    technologies: List[str]
    models: List[str]
    datasets: List[str]
    research_topics: List[str]
    general_keywords: List[str]


@router.post("/keywords", response_model=KeywordResponse)
async def extract_keywords(request: KeywordRequest):
    try:
        service = _get_service()
        keywords = service.extract_keywords(request.paper_text, request.top_k)
        return KeywordResponse(**keywords)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Keyword extraction failed: {str(e)}")
