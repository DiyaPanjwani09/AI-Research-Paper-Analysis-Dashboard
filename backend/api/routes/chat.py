from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

from services.rag_service import get_rag_service
from core.config import settings

router = APIRouter()


class ChatRequest(BaseModel):
    question: str = Field(..., min_length=1)
    paper_text: Optional[str] = None
    paper_id: Optional[str] = None
    sections: Optional[Dict[str, str]] = None
    title: Optional[str] = None
    top_k: int = Field(default=8, ge=1, le=50)
    rerank_top_k: int = Field(default=5, ge=1, le=20)
    chat_mode: str = Field(default="researcher")


class SourceChunk(BaseModel):
    chunk_id: str
    content: str
    section: str
    page: Optional[int]
    score: float


class ChatResponse(BaseModel):
    answer: str
    sources: List[SourceChunk]
    total_time: float = 0


@router.post("/chat", response_model=ChatResponse)
async def chat_with_paper(request: ChatRequest):
    try:
        rag = get_rag_service()

        if request.paper_text and request.paper_id:
            sections = request.sections or {"full_text": request.paper_text}
            rag.index_paper(
                document_id=request.paper_id,
                full_text=request.paper_text,
                sections=sections,
                title=request.title or "",
            )

        result = rag.query(
            question=request.question,
            top_k=request.top_k,
            rerank_top_k=request.rerank_top_k,
            filter_paper_id=request.paper_id,
        )

        sources = [
            SourceChunk(
                chunk_id=s["chunk_id"],
                content=s["content"][:500],
                section=s.get("section", ""),
                page=s.get("page"),
                score=s["score"],
            )
            for s in result["sources"]
        ]

        answer = result["answer"]
        if request.chat_mode == "student":
            answer = f"**Simple Explanation:**\n\n{answer}\n\n*Note: This is based on the paper content with technical details simplified.*"
        elif request.chat_mode == "beginner":
            answer = f"**In Simple Terms:**\n\n{answer}\n\n*Note: This explanation uses everyday language to describe the research.*"
        elif request.chat_mode == "executive":
            answer = f"**Executive Summary:**\n\n{answer}\n\n*Note: This focuses on high-level implications and business relevance.*"

        return ChatResponse(
            answer=answer,
            sources=sources,
            total_time=result.get("total_time", 0),
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chat failed: {str(e)}")
