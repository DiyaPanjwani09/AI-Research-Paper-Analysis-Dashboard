import numpy as np
import faiss
import logging
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)


class VectorStore:
    """FAISS-based vector store for document chunks."""

    def __init__(self, dimension: int = 384):
        self.dimension = dimension
        self.index = faiss.IndexFlatIP(dimension)
        self.chunk_map: List[Dict[str, Any]] = []

    def add(self, embeddings: np.ndarray, chunks: List[Dict[str, Any]]):
        if embeddings.shape[0] == 0:
            return
        if embeddings.shape[1] != self.dimension:
            logger.warning(f"Dimension mismatch: expected {self.dimension}, got {embedding.shape[1]}")
            return
        norms = np.linalg.norm(embeddings, axis=1, keepdims=True)
        norms[norms == 0] = 1.0
        normalized = embeddings / norms
        self.index.add(normalized.astype(np.float32))
        self.chunk_map.extend(chunks)

    def search(self, query_embedding: np.ndarray, top_k: int = 10) -> List[Dict[str, Any]]:
        if self.index.ntotal == 0:
            return []
        norms = np.linalg.norm(query_embedding, axis=1, keepdims=True)
        norms[norms == 0] = 1.0
        query_normalized = query_embedding / norms
        top_k = min(top_k, self.index.ntotal)
        scores, indices = self.index.search(query_normalized.astype(np.float32), top_k)
        results = []
        for score, idx in zip(scores[0], indices[0]):
            if idx != -1 and idx < len(self.chunk_map):
                results.append({
                    **self.chunk_map[idx],
                    "score": float(score),
                })
        return results

    def clear(self):
        self.index = faiss.IndexFlatIP(self.dimension)
        self.chunk_map = []

    @property
    def size(self) -> int:
        return self.index.ntotal
