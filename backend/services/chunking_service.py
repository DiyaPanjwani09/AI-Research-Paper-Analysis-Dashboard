import re
import uuid
from typing import List, Dict, Any, Optional
from dataclasses import dataclass


@dataclass
class Chunk:
    chunk_id: str
    content: str
    document_id: str
    section_name: str
    page_number: Optional[int]
    position: int

    def to_dict(self) -> Dict[str, Any]:
        return {
            "chunk_id": self.chunk_id,
            "content": self.content,
            "document_id": self.document_id,
            "section_name": self.section_name,
            "page_number": self.page_number,
            "position": self.position,
        }


class SemanticChunker:
    """Section-aware semantic chunking that respects document structure."""

    def __init__(self, chunk_size: int = 700, chunk_overlap: int = 100):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def chunk_paper(
        self,
        document_id: str,
        full_text: str,
        sections: Dict[str, str],
        pages: Optional[List[Dict]] = None,
    ) -> List[Chunk]:
        chunks = []
        position = 0

        section_page_map = {}
        if pages:
            for page_data in pages:
                page_text = page_data.get("text", "")
                page_num = page_data.get("page_number", 1)
                for section_name in sections:
                    if section_name not in section_page_map:
                        if sections[section_name][:200] in page_text:
                            section_page_map[section_name] = page_num

        section_order = [
            "abstract", "introduction", "related_work", "methodology",
            "experiments", "results", "discussion", "conclusion", "future_work",
        ]

        ordered_sections = []
        for name in section_order:
            if name in sections:
                ordered_sections.append((name, sections[name]))
        for name, content in sections.items():
            if name not in section_order:
                ordered_sections.append((name, content))

        for section_name, section_text in ordered_sections:
            section_chunks = self._chunk_section(section_text)
            for i, chunk_text in enumerate(section_chunks):
                chunk = Chunk(
                    chunk_id=f"{document_id}_chunk_{position}",
                    content=chunk_text,
                    document_id=document_id,
                    section_name=section_name,
                    page_number=section_page_map.get(section_name, 1),
                    position=position,
                )
                chunks.append(chunk)
                position += 1

        if not chunks and full_text:
            text_chunks = self._chunk_section(full_text)
            for i, chunk_text in enumerate(text_chunks):
                chunk = Chunk(
                    chunk_id=f"{document_id}_chunk_{position}",
                    content=chunk_text,
                    document_id=document_id,
                    section_name="full_text",
                    page_number=None,
                    position=position,
                )
                chunks.append(chunk)
                position += 1

        return chunks

    def _chunk_section(self, text: str) -> List[str]:
        words = text.split()
        if len(words) <= self.chunk_size:
            return [text] if text.strip() else []

        chunks = []
        i = 0
        while i < len(words):
            end = min(i + self.chunk_size, len(words))
            chunk_words = words[i:end]
            chunk_text = " ".join(chunk_words)

            if end < len(words):
                last_period = chunk_text.rfind('.')
                if last_period > self.chunk_size * 0.5:
                    chunk_text = chunk_text[:last_period + 1]
                    actual_words = chunk_text.split()
                    end = i + len(actual_words)

            chunks.append(chunk_text)
            i += max(1, end - i - self.chunk_overlap)

        return chunks
