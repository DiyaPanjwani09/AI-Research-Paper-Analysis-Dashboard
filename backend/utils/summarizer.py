import re
from typing import Dict, List
from sklearn.feature_extraction.text import TfidfVectorizer

# Lazy import of heavy deep-learning modules (optional)
try:
    from transformers import pipeline
    _HAS_TRANSFORMERS = True
except Exception:
    _HAS_TRANSFORMERS = False


class SmartSummarizer:
    """Generate summaries for research papers.

    Uses SciBERT (via transformers) when available and falls back to a
    TF-IDF / extractive summarization pipeline when the deep-learning
    stack is not installed.
    """

    def __init__(self, model_name: str = "allenai/scibert_scivocab_uncased"):
        self.model_name = model_name
        self.summarizer = None

        if _HAS_TRANSFORMERS:
            try:
                self.summarizer = pipeline("summarization", model=model_name)
            except Exception:
                try:
                    # Fallback to a generic summarization model
                    self.summarizer = pipeline("summarization")
                except Exception:
                    self.summarizer = None

    def generate_executive_summary(self, paper_text: str) -> str:
        """Generate an executive summary of the paper."""
        sections = self._extract_key_sections(paper_text)

        summary_text = ""
        if sections.get("abstract"):
            summary_text += sections["abstract"] + " "
        if sections.get("introduction"):
            summary_text += sections["introduction"][:800] + " "
        if sections.get("conclusion"):
            summary_text += sections["conclusion"]

        if not summary_text:
            summary_text = paper_text[:2500]

        if self.summarizer is not None:
            try:
                result = self.summarizer(
                    summary_text,
                    max_length=300,
                    min_length=80,
                    do_sample=False,
                )
                return result[0]["summary_text"]
            except Exception:
                pass

        return self._extractive_summary(summary_text, num_sentences=4)

    def generate_section_summaries(self, sections: Dict[str, str]) -> Dict[str, str]:
        """Generate summaries for each section."""
        section_summaries = {}

        for section_name, section_text in sections.items():
            if len(section_text) < 100:
                continue

            if self.summarizer is not None:
                try:
                    result = self.summarizer(
                        section_text,
                        max_length=120,
                        min_length=40,
                        do_sample=False,
                    )
                    section_summaries[section_name] = result[0]["summary_text"]
                    continue
                except Exception:
                    pass

            section_summaries[section_name] = self._extractive_summary(
                section_text, num_sentences=2
            )

        return section_summaries

    def extract_key_findings(self, paper_text: str) -> List[str]:
        """Extract key findings from the paper."""
        patterns = [
            r"we found that ([^.]+\.)",
            r"our results show that ([^.]+\.)",
            r"the main finding is that ([^.]+\.)",
            r"we demonstrate that ([^.]+\.)",
            r"we observed (?:that )?([^.]+\.)",
            r"results indicate (?:that )?([^.]+\.)",
        ]

        findings = []
        for pattern in patterns:
            matches = re.findall(pattern, paper_text, re.IGNORECASE)
            findings.extend([m.strip() for m in matches])

        return findings[:5]

    def extract_key_contributions(self, paper_text: str) -> List[str]:
        """Extract key contributions from the paper."""
        patterns = [
            r"our contribution (?:is|are) ([^.]+\.)",
            r"we contribute by ([^.]+\.)",
            r"the main contribution (?:is|are) ([^.]+\.)",
            r"this paper presents ([^.]+\.)",
            r"we propose ([^.]+\.)",
            r"we introduce ([^.]+\.)",
        ]

        contributions = []
        for pattern in patterns:
            matches = re.findall(pattern, paper_text, re.IGNORECASE)
            contributions.extend([m.strip() for m in matches])

        return contributions[:5]

    def _extract_key_sections(self, paper_text: str) -> Dict[str, str]:
        """Extract key sections from paper text."""
        sections = {}

        patterns = {
            "abstract": r"(?i)abstract[\s\n]*([^\n]+(?:\n[^\n]+)*)",
            "introduction": r"(?i)introduction[\s\n]*([^\n]+(?:\n[^\n]+){5,})",
            "methodology": r"(?i)method(?:ology)?[\s\n]*([^\n]+(?:\n[^\n]+){10,})",
            "results": r"(?i)results[\s\n]*([^\n]+(?:\n[^\n]+){10,})",
            "conclusion": r"(?i)conclusion[\s\n]*([^\n]+(?:\n[^\n]+){3,})",
        }

        for section_name, pattern in patterns.items():
            match = re.search(pattern, paper_text)
            if match:
                sections[section_name] = match.group(1).strip()

        return sections

    def _extractive_summary(self, text: str, num_sentences: int = 3) -> str:
        """Extractive summarization using TF-IDF sentence scoring."""
        sentences = [s.strip() for s in re.split(r"(?<=[.!?])\s+", text) if len(s.strip()) > 20]

        if len(sentences) <= num_sentences:
            return " ".join(sentences)

        try:
            vectorizer = TfidfVectorizer(
                stop_words="english",
                ngram_range=(1, 2),
                max_features=2000,
            )
            tfidf = vectorizer.fit_transform(sentences)
            scores = tfidf.sum(axis=1).A1
        except Exception:
            # Even simpler fallback: score by word frequency
            scores = [len(s.split()) for s in sentences]

        ranked = sorted(range(len(sentences)), key=lambda i: scores[i], reverse=True)
        top_indices = sorted(ranked[:num_sentences])

        summary = " ".join(sentences[i] for i in top_indices)
        return summary if summary.endswith(".") else summary + "."
