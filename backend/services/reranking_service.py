import numpy as np
import logging
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)

_HAS_CROSS_ENCODER = False
CrossEncoder = None

try:
    from sentence_transformers import CrossEncoder as _CE
    CrossEncoder = _CE
    _HAS_CROSS_ENCODER = True
except ImportError:
    pass


class RerankerService:
    """Cross-encoder reranking service for improving retrieval quality."""

    def __init__(self, model_name: str = "cross-encoder/ms-marco-MiniLM-L-6-v2"):
        self.model_name = model_name
        self.model = None
        self._loaded = False

    def load(self):
        if self._loaded:
            return
        if _HAS_CROSS_ENCODER:
            try:
                self.model = CrossEncoder(self.model_name)
                self._loaded = True
                logger.info(f"Loaded reranker model: {self.model_name}")
            except Exception as e:
                logger.warning(f"Failed to load reranker {self.model_name}: {e}")
                self._loaded = True
        else:
            logger.warning("CrossEncoder not available, reranking will use original scores")
            self._loaded = True

    def rerank(
        self,
        query: str,
        results: List[Dict[str, Any]],
        top_k: int = 5,
        content_key: str = "content",
    ) -> List[Dict[str, Any]]:
        if not results:
            return []

        self.load()

        if self.model is None:
            return results[:top_k]

        pairs = [(query, r.get(content_key, "")[:512]) for r in results]
        try:
            scores = self.model.predict(pairs)
            for i, score in enumerate(scores):
                results[i]["rerank_score"] = float(score)
            results.sort(key=lambda x: x.get("rerank_score", 0), reverse=True)
        except Exception as e:
            logger.warning(f"Reranking failed: {e}")

        return results[:top_k]
