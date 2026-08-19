from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import List

from services.gap_detection_service import get_gap_service

router = APIRouter()


class GapRequest(BaseModel):
    paper_text: str = Field(..., min_length=100)


class GapItem(BaseModel):
    gap: str
    evidence: str
    category: str
    severity: str
    confidence: float
    type: str


class GapResponse(BaseModel):
    gaps: List[GapItem]
    total_count: int


@router.post("/gaps", response_model=GapResponse)
async def detect_research_gaps(request: GapRequest):
    try:
        service = get_gap_service()
        gaps = service.detect_gaps(request.paper_text)
        gap_items = [GapItem(**g) for g in gaps]
        return GapResponse(gaps=gap_items, total_count=len(gap_items))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Gap detection failed: {str(e)}")
