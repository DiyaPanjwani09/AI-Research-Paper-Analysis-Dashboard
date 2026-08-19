import re
from typing import Dict, List
from sklearn.feature_extraction.text import TfidfVectorizer

_HAS_KEYBERT = False
try:
    from keybert import KeyBERT
    _HAS_KEYBERT = True
except ImportError:
    pass

_HAS_SPACY = False
try:
    import spacy
    _HAS_SPACY = True
except ImportError:
    pass


RESEARCH_TERMS = {
    "technologies": [
        "machine learning", "deep learning", "nlp", "computer vision",
        "reinforcement learning", "transfer learning", "natural language processing",
        "generative ai", "foundation model", "self-supervised learning",
    ],
    "models": [
        "bert", "gpt", "transformer", "cnn", "rnn", "lstm", "resnet",
        "neural network", "xgboost", "random forest", "diffusion model",
        "vae", "gan", "attention mechanism", "vision transformer",
    ],
    "datasets": [
        "imagenet", "cifar", "mnist", "glue", "squad", "wikitext",
        "arxiv", "pubmed", "common crawl", "openwebtext",
    ],
}


class KeywordExtractionService:
    def __init__(self):
        self.kw_model = None
        if _HAS_KEYBERT:
            try:
                self.kw_model = KeyBERT()
            except Exception:
                pass

        self.nlp = None
        if _HAS_SPACY:
            try:
                self.nlp = spacy.load("en_core_web_sm")
            except Exception:
                pass

    def extract_keywords(self, text: str, top_k: int = 20) -> Dict[str, List[str]]:
        cleaned = self._preprocess(text)

        all_kw = []
        if self.kw_model:
            try:
                kw = self.kw_model.extract_keywords(
                    cleaned,
                    keyphrase_ngram_range=(1, 2),
                    stop_words="english",
                    top_n=top_k,
                )
                all_kw.extend([k[0] for k in kw])
            except Exception:
                pass

        all_kw.extend(self._tfidf_keywords(cleaned, top_k))
        all_kw = list(dict.fromkeys(all_kw))

        domain = self._domain_keywords(cleaned)
        categorized = {
            "technologies": self._match_category(all_kw, "technologies"),
            "models": self._match_category(all_kw, "models"),
            "datasets": self._match_category(all_kw, "datasets"),
            "research_topics": self._research_topics(all_kw),
            "general_keywords": all_kw[:top_k],
        }
        for cat, terms in domain.items():
            categorized[cat] = list(dict.fromkeys(categorized.get(cat, []) + terms))

        return categorized

    def _preprocess(self, text: str) -> str:
        text = re.sub(r'\[\d+\]', '', text)
        text = re.sub(r'http\S+', ' ', text)
        return re.sub(r'\s+', ' ', text).strip()

    def _tfidf_keywords(self, text: str, top_k: int) -> List[str]:
        try:
            v = TfidfVectorizer(ngram_range=(1, 2), stop_words="english", max_features=top_k)
            X = v.fit_transform([text])
            names = v.get_feature_names_out()
            scores = X.toarray()[0]
            idx = scores.argsort()[::-1]
            return [names[i] for i in idx[:top_k]]
        except Exception:
            return []

    def _domain_keywords(self, text: str) -> Dict[str, List[str]]:
        result = {cat: [] for cat in RESEARCH_TERMS}
        lowered = text.lower()
        for cat, terms in RESEARCH_TERMS.items():
            for t in terms:
                if t.lower() in lowered:
                    result[cat].append(t)
        return result

    def _match_category(self, keywords: List[str], category: str) -> List[str]:
        if category not in RESEARCH_TERMS:
            return []
        cat_terms = RESEARCH_TERMS[category]
        return [kw for kw in keywords if any(t in kw.lower() for t in cat_terms)]

    def _research_topics(self, keywords: List[str]) -> List[str]:
        patterns = [
            r".*analysis", r".*learning", r".*model", r".*network",
            r".*algorithm", r".*framework", r".*method", r".*system",
        ]
        return [kw for kw in keywords if any(re.match(p, kw) for p in patterns)]
