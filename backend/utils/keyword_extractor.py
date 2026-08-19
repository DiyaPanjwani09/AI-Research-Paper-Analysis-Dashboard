import re
from typing import List, Dict

try:
    import spacy
    _HAS_SPACY = True
except Exception:
    _HAS_SPACY = False

try:
    from keybert import KeyBERT
    _HAS_KEYBERT = True
except Exception:
    _HAS_KEYBERT = False

from sklearn.feature_extraction.text import TfidfVectorizer


class KeywordExtractor:
    """Extract keywords from research papers.

    Uses KeyBERT + spaCy when available, and falls back to a TF-IDF based
    extraction pipeline otherwise.
    """

    def __init__(self):
        self.nlp = None
        if _HAS_SPACY:
            try:
                self.nlp = spacy.load("en_core_web_sm")
            except OSError:
                try:
                    spacy.cli.download("en_core_web_sm")
                    self.nlp = spacy.load("en_core_web_sm")
                except Exception:
                    self.nlp = None
            except Exception:
                self.nlp = None

        self.kw_model = None
        if _HAS_KEYBERT:
            try:
                self.kw_model = KeyBERT()
            except Exception:
                self.kw_model = None

        self.research_terms = {
            "technologies": [
                "machine learning", "deep learning", "nlp", "computer vision",
                "reinforcement learning", "transfer learning", "natural language processing",
            ],
            "models": [
                "bert", "gpt", "transformer", "cnn", "rnn", "lstm", "resnet",
                "neural network", "xgboost", "random forest",
            ],
            "datasets": [
                "imagenet", "cifar", "mnist", "glue", "squad", "wikitext",
                "arxiv", "scientific", "wikipedia",
            ],
        }

    def extract_keywords(self, text: str, top_k: int = 20) -> Dict[str, List[str]]:
        """Extract keywords categorized by type."""
        cleaned_text = self._preprocess_text(text)

        all_keywords = []
        if self.kw_model is not None:
            try:
                kw = self.kw_model.extract_keywords(
                    cleaned_text,
                    keyphrase_ngram_range=(1, 2),
                    stop_words="english",
                    top_n=top_k,
                )
                all_keywords.extend([k[0] for k in kw])
            except Exception:
                pass

        all_keywords.extend(self._extract_with_tfidf(cleaned_text, top_k))
        all_keywords = list(dict.fromkeys(all_keywords))

        domain_keywords = self._extract_domain_specific(cleaned_text)

        categorized = {
            "technologies": self._categorize_keywords(all_keywords, "technologies"),
            "models": self._categorize_keywords(all_keywords, "models"),
            "datasets": self._categorize_keywords(all_keywords, "datasets"),
            "research_topics": self._extract_research_topics(all_keywords),
            "general_keywords": all_keywords[:top_k],
        }

        for category, terms in domain_keywords.items():
            categorized[category] = list(dict.fromkeys(categorized[category] + terms))

        return categorized

    def _preprocess_text(self, text: str) -> str:
        text = re.sub(r"\[\d+\]", "", text)
        text = re.sub(r"http\S+", " ", text)
        text = re.sub(r"\s+", " ", text)
        return text

    def _extract_with_tfidf(self, text: str, top_k: int) -> List[str]:
        try:
            vectorizer = TfidfVectorizer(
                ngram_range=(1, 2), stop_words="english", max_features=top_k
            )
            X = vectorizer.fit_transform([text])
            feature_names = vectorizer.get_feature_names_out()
            scores = X.toarray()[0]
            sorted_idx = scores.argsort()[::-1]
            return [feature_names[i] for i in sorted_idx[:top_k]]
        except Exception:
            return []

    def _extract_domain_specific(self, text: str) -> Dict[str, List[str]]:
        domain_keywords = {category: [] for category in self.research_terms}
        lowered = text.lower()
        for category, terms in self.research_terms.items():
            for term in terms:
                if term.lower() in lowered:
                    domain_keywords[category].append(term)
        return domain_keywords

    def _categorize_keywords(self, keywords: List[str], category: str) -> List[str]:
        if category not in self.research_terms:
            return []
        category_terms = self.research_terms[category]
        return [kw for kw in keywords if any(t in kw.lower() for t in category_terms)]

    def _extract_research_topics(self, keywords: List[str]) -> List[str]:
        patterns = [
            r".*analysis", r".*learning", r".*model", r".*network",
            r".*algorithm", r".*framework", r".*method", r".*system",
            r".*recognition", r".*classification", r".*prediction",
        ]
        return [kw for kw in keywords if any(re.match(p, kw) for p in patterns)]
