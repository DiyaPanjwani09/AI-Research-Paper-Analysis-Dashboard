import os
import uuid
import logging
from datetime import datetime, timezone
from typing import Dict, Any, Optional

from utils.pdf_parser import PDFParser
from services.summarization_service import get_summarization_service
from services.rag_service import get_rag_service
from services.gap_detection_service import get_gap_service
from core.config import settings

logger = logging.getLogger(__name__)


class DocumentService:
    """Orchestrates the full document processing pipeline."""

    def __init__(self):
        self.pdf_parser = PDFParser()
        self.summarizer = get_summarization_service()
        self.rag_service = get_rag_service()

    async def process_upload(self, file_path: str, filename: str) -> Dict[str, Any]:
        file_id = str(uuid.uuid4())

        try:
            metadata = self.pdf_parser.parse_pdf(file_path)
        except Exception as e:
            logger.error(f"PDF parsing failed for {filename}: {e}")
            raise ValueError(f"Unable to parse PDF: {str(e)}")

        section_dict = metadata.sections
        if not section_dict:
            section_dict = {"full_text": metadata.full_text}
            metadata.sections = section_dict

        executive_summary = self.summarizer.generate_executive_summary(
            sections=section_dict,
            full_text=metadata.full_text,
        )

        section_summaries = {}
        if section_dict:
            section_summaries = self.summarizer.generate_section_summaries(section_dict)

        key_findings = self.summarizer.extract_key_findings(metadata.full_text)
        key_contributions = self.summarizer.extract_key_contributions(metadata.full_text)

        try:
            self.rag_service.index_paper(
                document_id=file_id,
                full_text=metadata.full_text,
                sections=section_dict,
                title=metadata.title,
            )
        except Exception as e:
            logger.warning(f"Failed to index paper for RAG: {e}")

        response = {
            "file_id": file_id,
            "status": "completed",
            "metadata": {
                "title": metadata.title,
                "authors": metadata.authors,
                "abstract": metadata.abstract,
                "keywords": metadata.keywords,
                "year": metadata.year,
                "venue": metadata.venue,
                "doi": metadata.doi,
                "page_count": metadata.page_count,
                "word_count": metadata.word_count,
            },
            "sections": list(metadata.sections.keys()),
            "summaries": {
                "executive_summary": executive_summary,
                "section_summaries": section_summaries,
                "key_findings": key_findings,
                "key_contributions": key_contributions,
            },
            "full_text": metadata.full_text[:5000],
        }

        return response

    def get_paper_text(self, file_path: str) -> str:
        metadata = self.pdf_parser.parse_pdf(file_path)
        return metadata.full_text


_document_service: Optional[DocumentService] = None


def get_document_service() -> DocumentService:
    global _document_service
    if _document_service is None:
        _document_service = DocumentService()
    return _document_service
