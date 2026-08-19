from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any, Optional

from services.recommendation_service import RecommendationService
from services.embedding_service import get_embedding_service
from services.vector_store import VectorStore

router = APIRouter()

_recommendation_service: RecommendationService = None


def _get_service() -> RecommendationService:
    global _recommendation_service
    if _recommendation_service is None:
        _recommendation_service = RecommendationService()
    return _recommendation_service


class RecommendationRequest(BaseModel):
    paper_text: str
    paper_id: Optional[str] = None
    top_k: int = 5


class SimilarPaper(BaseModel):
    paper_id: str
    title: str
    abstract: str
    authors: str
    similarity_score: float
    reasons: List[str] = []


class RecommendationResponse(BaseModel):
    similar_papers: List[SimilarPaper]
    total_papers_in_db: int = 0


@router.post("/recommend", response_model=RecommendationResponse)
async def recommend_similar_papers(request: RecommendationRequest):
    try:
        service = _get_service()
        results = service.get_recommendations(request.paper_text, request.top_k)
        papers = [
            SimilarPaper(
                paper_id=r["paper_id"],
                title=r["title"],
                abstract=r["abstract"],
                authors=r["authors"],
                similarity_score=r["similarity_score"],
                reasons=r["reasons"],
            )
            for r in results
        ]
        return RecommendationResponse(
            similar_papers=papers,
            total_papers_in_db=len(service.papers),
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Recommendation failed: {str(e)}")
