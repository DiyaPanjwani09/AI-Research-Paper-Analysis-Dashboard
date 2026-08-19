import re
import logging
from typing import Dict, List

logger = logging.getLogger(__name__)

_HAS_SPACY = False
try:
    import spacy
    _HAS_SPACY = True
except ImportError:
    pass


GAP_CATEGORIES = {
    "limitation": "Method Limitation",
    "drawback": "Method Limitation",
    "shortcoming": "Method Limitation",
    "dataset": "Dataset Limitation",
    "computational": "Computational Limitation",
    "scalab": "Scalability Limitation",
    "generalization": "Generalization Limitation",
    "evaluation": "Evaluation Limitation",
    "reproducib": "Reproducibility Limitation",
    "domain": "Domain Limitation",
}

SEVERITY_KEYWORDS = {
    "High": ["critical", "major", "significant", "fundamental", "severe"],
    "Medium": ["important", "notable", "considerable", "substantial"],
    "Low": ["minor", "small", "slight", "limited"],
}


class GapDetectionService:
    """Structured research gap detection with categorization and severity."""

    def __init__(self):
        self.nlp = None
        if _HAS_SPACY:
            try:
                self.nlp = spacy.load("en_core_web_sm")
            except Exception:
                pass

    def detect_gaps(self, paper_text: str) -> List[Dict]:
        sentences = self._split_sentences(paper_text)
        gaps = []

        gap_patterns = {
            "limitation": [
                r"(?:limitation|drawback|shortcoming|weakness|disadvantage)[^.]*(?:\.|$)",
                r"(?:however|although|but)[^.]*limitation",
                r"(?:one|another|a major|a significant) limitation",
                r"(?:not(?:able|) (?:address|consider|handl|account))[^.]*",
            ],
            "future_work": [
                r"(?:future work|future research|future study|future direction)[^.]*(?:\.|$)",
                r"(?:suggest|recommend)[^.]*future",
                r"(?:would be interesting|worth exploring|worth investigating)[^.]*(?:\.|$)",
                r"(?:potential|promising) direction[^.]*(?:\.|$)",
                r"(?:call for|need for) further (?:research|investigation|study)[^.]*(?:\.|$)",
            ],
            "open_problem": [
                r"(?:open problem|open question|unresolved issue|open challenge)[^.]*(?:\.|$)",
                r"(?:remain|still) (?:unanswered|unresolved|open|unsolved)[^.]*(?:\.|$)",
                r"(?:requires|needs) further (?:investigation|study|work|research)[^.]*(?:\.|$)",
                r"(?:not yet|not fully|not completely) (?:understood|solved|addressed|explored)[^.]*(?:\.|$)",
            ],
            "data_gap": [
                r"(?:lack(?:ing)?|insufficient|limited|scarce|absent) (?:of )?(?:data|dataset|annotation|labeled)[^.]*(?:\.|$)",
                r"(?:small|bias|unrepresentative) dataset[^.]*(?:\.|$)",
            ],
        }

        for sentence in sentences:
            for gap_type, patterns in gap_patterns.items():
                for pattern in patterns:
                    if re.search(pattern, sentence, re.IGNORECASE):
                        category = self._categorize_gap(sentence)
                        severity = self._assess_severity(sentence)
                        confidence = self._compute_confidence(sentence, gap_type)
                        gaps.append({
                            "gap": sentence.strip(),
                            "evidence": sentence.strip(),
                            "category": category,
                            "severity": severity,
                            "confidence": confidence,
                            "type": gap_type,
                        })
                        break

        seen = set()
        unique_gaps = []
        for gap in gaps:
            key = gap["gap"][:100]
            if key not in seen:
                seen.add(key)
                unique_gaps.append(gap)

        return unique_gaps[:20]

    def _split_sentences(self, text: str) -> List[str]:
        if self.nlp:
            try:
                doc = self.nlp(text[:100000])
                return [sent.text for sent in doc.sents]
            except Exception:
                pass
        return [s.strip() for s in re.split(r'(?<=[.!?])\s+', text) if s.strip()]

    def _categorize_gap(self, sentence: str) -> str:
        lower = sentence.lower()
        for keyword, category in GAP_CATEGORIES.items():
            if keyword in lower:
                return category
        return "General Limitation"

    def _assess_severity(self, sentence: str) -> str:
        lower = sentence.lower()
        for severity, keywords in SEVERITY_KEYWORDS.items():
            if any(kw in lower for kw in keywords):
                return severity
        return "Medium"

    def _compute_confidence(self, sentence: str, gap_type: str) -> float:
        base = 0.6
        if any(w in sentence.lower() for w in ["major", "critical", "significant", "fundamental"]):
            base += 0.2
        if any(w in sentence.lower() for w in ["we", "our", "this paper", "our work"]):
            base += 0.1
        if gap_type in ("limitation", "future_work"):
            base += 0.1
        return min(base, 0.95)


_gap_service: Optional[GapDetectionService] = None


def get_gap_service() -> GapDetectionService:
    global _gap_service
    if _gap_service is None:
        _gap_service = GapDetectionService()
    return _gap_service
