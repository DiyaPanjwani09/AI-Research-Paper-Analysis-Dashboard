import re
from typing import List, Dict

try:
    import spacy
    _HAS_SPACY = True
except Exception:
    _HAS_SPACY = False


class ResearchGapDetector:
    """Detect research gaps, limitations, and future work in papers.

    Uses spaCy sentence segmentation when available and falls back to
    regex-based sentence splitting otherwise.
    """

    def __init__(self):
        self.nlp = None
        if _HAS_SPACY:
            try:
                self.nlp = spacy.load("en_core_web_sm")
            except Exception:
                self.nlp = None

        self.limitation_patterns = [
            r"(?:limitation|drawback|shortcoming|weakness)[^.]*",
            r"(?:however|although|but)[^.]*limitation",
            r"(?:major|significant|important) limitation",
            r"(?:study|research|paper) (?:has|have) limitation",
            r"(?:one|another) limitation (?:is|are)",
        ]

        self.future_work_patterns = [
            r"(?:future work|future research|future study)[^.]*",
            r"(?:suggest|recommend)[^.]*future",
            r"(?:would be interesting|worth exploring)[^.]*",
            r"(?:potential|promising) direction",
            r"(?:call for|need for) future research",
        ]

        self.open_problem_patterns = [
            r"(?:open problem|open question|unresolved issue)[^.]*",
            r"(?:remain|still) (?:unanswered|unresolved|open)",
            r"(?:challenge|difficulty|problem)[^.]*",
            r"(?:requires|needs) further (?:investigation|study)",
            r"(?:not yet|not fully) (?:understood|solved|addressed)",
        ]

    def _split_sentences(self, text: str) -> List[str]:
        """Split text into sentences (spaCy if available, regex otherwise)."""
        if self.nlp is not None:
            try:
                doc = self.nlp(text)
                return [sent.text for sent in doc.sents]
            except Exception:
                pass
        return [s.strip() for s in re.split(r"(?<=[.!?])\s+", text) if s.strip()]

    def detect_gaps(self, paper_text: str) -> Dict[str, List[str]]:
        """Detect research gaps, limitations, and future work."""
        limitations = self._extract_patterns(paper_text, self.limitation_patterns)
        future_research = self._extract_patterns(paper_text, self.future_work_patterns)
        open_problems = self._extract_patterns(paper_text, self.open_problem_patterns)

        return {
            "limitations": limitations,
            "future_research": future_research,
            "open_problems": open_problems,
        }

    def _extract_patterns(self, text: str, patterns: List[str]) -> List[str]:
        """Extract sentences matching any of the given patterns."""
        matches = []
        for sentence in self._split_sentences(text):
            if any(re.search(p, sentence, re.IGNORECASE) for p in patterns):
                matches.append(sentence.strip())
        return matches[:10]

    def generate_future_research_suggestions(self, paper_text: str) -> List[str]:
        """Generate potential future research directions."""
        key_concepts = self._extract_key_concepts(paper_text)

        if not key_concepts:
            return [
                "Scaling the proposed approach to larger datasets",
                "Exploring generalization across domains",
                "Improving computational efficiency",
            ]

        templates = [
            "Extending {c} to multi-modal applications",
            "Applying {c} in real-world scenarios",
            "Investigating the scalability of {c}",
            "Exploring {c} in different domains",
            "Comparative study of {c} with alternative approaches",
            "Long-term impact analysis of {c}",
            "Ethical considerations in {c} implementation",
            "Optimizing {c} for resource-constrained environments",
        ]

        suggestions = []
        for concept in key_concepts:
            suggestions.extend(t.format(c=concept) for t in templates)

        return list(dict.fromkeys(suggestions))[:10]

    def _extract_key_concepts(self, text: str) -> List[str]:
        """Extract key concepts from paper text."""
        sentences = self._split_sentences(text)

        # Simple frequency-based phrase extraction
        concept_freq = {}
        for sentence in sentences:
            for match in re.finditer(
                r"\b([A-Z][a-z]+(?:\s+[a-z]+){1,4})\b", sentence
            ):
                phrase = match.group(1)
                if len(phrase.split()) > 1:
                    concept_freq[phrase] = concept_freq.get(phrase, 0) + 1

        sorted_concepts = sorted(concept_freq.items(), key=lambda x: x[1], reverse=True)
        return [concept for concept, _ in sorted_concepts[:5]]
