import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.pdf_parser import PDFParser
from services.chunking_service import SemanticChunker
from services.gap_detection_service import GapDetectionService


class TestPDFParser:
    def test_init(self):
        parser = PDFParser()
        assert parser is not None

    def test_section_header_detection(self):
        parser = PDFParser()
        assert parser._is_section_header("1. Introduction") is not None
        assert parser._is_section_header("Methodology") is not None
        assert parser._is_section_header("This is a very long line that should not be a section header because it exceeds one hundred characters in length easily") is None


class TestChunker:
    def test_chunk_small_text(self):
        chunker = SemanticChunker(chunk_size=700, chunk_overlap=100)
        chunks = chunker.chunk_paper("doc1", "Short text.", {"abstract": "Short text."})
        assert len(chunks) >= 1
        assert chunks[0].document_id == "doc1"

    def test_chunk_large_text(self):
        chunker = SemanticChunker(chunk_size=50, chunk_overlap=10)
        text = " ".join(["word"] * 200)
        sections = {"introduction": text}
        chunks = chunker.chunk_paper("doc1", text, sections)
        assert len(chunks) > 1

    def test_chunk_preserves_metadata(self):
        chunker = SemanticChunker(chunk_size=50, chunk_overlap=10)
        text = " ".join(["word"] * 200)
        sections = {"methodology": text}
        chunks = chunker.chunk_paper("doc1", text, sections)
        for chunk in chunks:
            assert chunk.document_id == "doc1"
            assert chunk.section_name == "methodology"


class TestGapDetector:
    def test_detect_gaps(self):
        detector = GapDetectionService()
        text = "One major limitation of this approach is the computational cost. Future work should address scalability issues."
        gaps = detector.detect_gaps(text)
        assert len(gaps) > 0
        assert any("limitation" in g["gap"].lower() or "future" in g["gap"].lower() for g in gaps)

    def test_no_gaps(self):
        detector = GapDetectionService()
        text = "The experiment was conducted successfully with positive results across all metrics."
        gaps = detector.detect_gaps(text)
        assert len(gaps) == 0
