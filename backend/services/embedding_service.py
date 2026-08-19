import numpy as np
import logging
from typing import List, Optional

logger = logging.getLogger(__name__)

_HAS_ST = False
SentenceTransformer = None

try:
    from sentence_transformers import SentenceTransformer as _ST
    SentenceTransformer = _ST
    _HAS_ST = True
except ImportError:
    pass


class EmbeddingService:
    """Configurable embedding service with automatic dimension detection."""

    def __init__(self, model_name: str = "sentence-transformers/all-MiniLM-L6-v2"):
        self.model_name = model_name
        self.model = None
        self.dimension = 0
        self._loaded = False

    def load(self):
        if self._loaded:
            return
        if _HAS_ST:
            try:
                self.model = SentenceTransformer(self.model_name)
                test = self.model.encode(["test"])
                self.dimension = test.shape[1]
                self._loaded = True
                logger.info(f"Loaded embedding model: {self.model_name} (dim={self.dimension})")
            except Exception as e:
                logger.warning(f"Failed to load {self.model_name}: {e}")
                self.dimension = 384
                self._loaded = True
        else:
            logger.warning("sentence-transformers not available, using TF-IDF fallback")
            self.dimension = 512
            self._loaded = True

    def encode(self, texts: List[str]) -> np.ndarray:
        self.load()
        if self.model is not None:
            return self.model.encode(texts, show_progress_bar=False).astype(np.float32)
        return self._tfidf_encode(texts)

    def encode_query(self, query: str) -> np.ndarray:
        return self.encode([query])

    def _tfidf_encode(self, texts: List[str]) -> np.ndarray:
        from sklearn.feature_extraction.text import TfidfVectorizer
        vectorizer = TfidfVectorizer(
            stop_words="english",
            ngram_range=(1, 2),
            max_features=self.dimension,
        )
        vectors = vectorizer.fit_transform(texts).toarray().astype(np.float32)
        norms = np.linalg.norm(vectors, axis=1, keepdims=True)
        norms[norms == 0] = 1.0
        return vectors / norms


_embedding_service: Optional[EmbeddingService] = None


def get_embedding_service(model_name: str = "sentence-transformers/all-MiniLM-L6-v2") -> EmbeddingService:
    global _embedding_service
    if _embedding_service is None:
        _embedding_service = EmbeddingService(model_name)
    return _embedding_service
