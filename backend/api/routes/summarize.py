from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Dict, List

from services.summarization_service import get_summarization_service

router = APIRouter()


class SummarizationRequest(BaseModel):
    paper_text: str = Field(..., min_length=100)
    sections: Dict[str, str] = Field(default_factory=dict)
    include_sections: bool = True
    include_findings: bool = True
    include_contributions: bool = True


class SummarizationResponse(BaseModel):
    executive_summary: str
    section_summaries: Dict[str, str]
    key_findings: List[str]
    key_contributions: List[str]


@router.post("/summarize", response_model=SummarizationResponse)
async def summarize_paper(request: SummarizationRequest):
    try:
        service = get_summarization_service()

        sections = request.sections
        if not sections:
            sections = {"full_text": request.paper_text}

        executive = service.generate_executive_summary(sections, request.paper_text)

        section_summaries = {}
        if request.include_sections and sections:
            section_summaries = service.generate_section_summaries(sections)

        findings = service.extract_key_findings(request.paper_text) if request.include_findings else []
        contributions = service.extract_key_contributions(request.paper_text) if request.include_contributions else []

        return SummarizationResponse(
            executive_summary=executive,
            section_summaries=section_summaries,
            key_findings=findings,
            key_contributions=contributions,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Summarization failed: {str(e)}")
