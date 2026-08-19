from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, List, Any, Optional

from services.trend_service import get_trend_service

router = APIRouter()


class TrendRequest(BaseModel):
    time_period: str = "monthly"
    papers: List[Dict[str, Any]] = []


class TrendResponse(BaseModel):
    topic_frequency: Dict[str, int]
    research_growth: Dict[str, int]
    emerging_topics: List[str]
    top_categories: List[str]
    publication_trends: Dict


@router.post("/analytics/trends", response_model=TrendResponse)
async def analyze_research_trends(request: TrendRequest):
    try:
        service = get_trend_service()
        result = service.analyze(request.papers)
        return TrendResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Trend analysis failed: {str(e)}")


@router.get("/analytics/stats")
async def get_analytics_stats():
    try:
        service = get_trend_service()
        stats = service.compute_stats([])
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Stats failed: {str(e)}")


@router.post("/search")
async def semantic_search(query: str, top_k: int = 5):
    try:
        from services.rag_service import get_rag_service
        rag = get_rag_service()
        result = rag.query(query, top_k=top_k, rerank_top_k=top_k)
        return {
            "query": query,
            "results": result["sources"],
            "total_time": result.get("total_time", 0),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")
