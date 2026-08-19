import re
import logging
from typing import Dict, List, Optional
from sklearn.feature_extraction.text import TfidfVectorizer
import numpy as np

logger = logging.getLogger(__name__)

_HAS_TRANSFORMERS = False
pipeline_fn = None

try:
    from transformers import pipeline as _pipeline
    pipeline_fn = _pipeline
    _HAS_TRANSFORMERS = True
except ImportError:
    pass


class SummarizationService:
    """Hierarchical summarization: section summaries -> executive summary."""

    def __init__(self, model_name: str = "facebook/bart-large-cnn"):
        self.model_name = model_name
        self.summarizer = None
        self._loaded = False

    def load(self):
        if self._loaded:
            return
        if _HAS_TRANSFORMERS:
            try:
                self.summarizer = pipeline_fn(
                    "summarization",
                    model=self.model_name,
                    max_length=512,
                    min_length=50,
                )
                logger.info(f"Loaded summarization model: {self.model_name}")
            except Exception as e:
                logger.warning(f"Failed to load summarization model {self.model_name}: {e}")
                try:
                    self.summarizer = pipeline_fn("summarization")
                    logger.info("Loaded fallback summarization model")
                except Exception:
                    logger.warning("No summarization model available, using extractive only")
        self._loaded = True

    def summarize(self, text: str, max_length: int = 300, min_length: int = 80) -> str:
        self.load()
        if self.summarizer and len(text) > 200:
            try:
                truncated = text[:2000]
                result = self.summarizer(
                    truncated,
                    max_length=max_length,
                    min_length=min_length,
                    do_sample=False,
                )
                return result[0]["summary_text"]
            except Exception as e:
                logger.warning(f"Generative summarization failed: {e}")
        return self._extractive_summary(text, num_sentences=5)

    def generate_section_summaries(self, sections: Dict[str, str]) -> Dict[str, str]:
        summaries = {}
        for name, text in sections.items():
            if len(text) < 100:
                summaries[name] = text
                continue
            summaries[name] = self.summarize(text, max_length=150, min_length=30)
        return summaries

    def generate_executive_summary(self, sections: Dict[str, str], full_text: str) -> str:
        parts = []
        if "abstract" in sections:
            parts.append(sections["abstract"])
        if "introduction" in sections:
            parts.append(sections["introduction"][:500])
        if "conclusion" in sections:
            parts.append(sections["conclusion"][:500])
        if "results" in sections:
            parts.append(sections["results"][:500])

        combined = " ".join(parts) if parts else full_text[:2000]
        return self.summarize(combined, max_length=300, min_length=80)

    def _extractive_summary(self, text: str, num_sentences: int = 5) -> str:
        sentences = [s.strip() for s in re.split(r'(?<=[.!?])\s+', text) if len(s.strip()) > 20]
        if len(sentences) <= num_sentences:
            return " ".join(sentences)
        try:
            vectorizer = TfidfVectorizer(stop_words="english", ngram_range=(1, 2), max_features=2000)
            tfidf = vectorizer.fit_transform(sentences)
            scores = tfidf.sum(axis=1).A1
        except Exception:
            scores = np.array([len(s.split()) for s in sentences], dtype=float)

        ranked = sorted(range(len(sentences)), key=lambda i: scores[i], reverse=True)
        top_indices = sorted(ranked[:num_sentences])
        summary = " ".join(sentences[i] for i in top_indices)
        return summary if summary.endswith(".") else summary + "."

    def extract_key_findings(self, text: str) -> List[str]:
        patterns = [
            r"we found that ([^.]+\.)",
            r"our results show that ([^.]+\.)",
            r"the main finding is that ([^.]+\.)",
            r"we demonstrate that ([^.]+\.)",
            r"we observed (?:that )?([^.]+\.)",
            r"results indicate (?:that )?([^.]+\.)",
            r"achieved (?:an? )?([^,.]+)",
        ]
        findings = []
        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            findings.extend([m.strip() for m in matches])
        return list(dict.fromkeys(findings))[:7]

    def extract_key_contributions(self, text: str) -> List[str]:
        patterns = [
            r"our contribution (?:is|are) ([^.]+\.)",
            r"we contribute by ([^.]+\.)",
            r"the main contribution (?:is|are) ([^.]+\.)",
            r"this paper presents ([^.]+\.)",
            r"we propose ([^.]+\.)",
            r"we introduce ([^.]+\.)",
            r"we (?:develop|design|build) ([^.]+\.)",
        ]
        contributions = []
        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            contributions.extend([m.strip() for m in matches])
        return list(dict.fromkeys(contributions))[:7]


_summarization_service: Optional[SummarizationService] = None


def get_summarization_service() -> SummarizationService:
    global _summarization_service
    if _summarization_service is None:
        _summarization_service = SummarizationService()
    return _summarization_service
