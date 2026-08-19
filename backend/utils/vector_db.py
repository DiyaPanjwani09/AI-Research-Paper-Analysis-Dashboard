import faiss
import numpy as np
import json
import os
from typing import List, Dict, Any
from sklearn.feature_extraction.text import TfidfVectorizer

try:
    from sentence_transformers import SentenceTransformer
    _HAS_ST = True
except Exception:
    _HAS_ST = False


class VectorDB:
    """Vector search over research papers using FAISS.

    Uses SentenceTransformer embeddings when available and falls back to
    TF-IDF vectors otherwise.
    """

    def __init__(
        self,
        index_path: str = "vector_db/faiss_index",
        model_name: str = "sentence-transformers/all-MiniLM-L6-v2",
    ):
        self.index_path = index_path
        self.model_name = model_name
        self.model = None
        self.tfidf = None

        if _HAS_ST:
            try:
                self.model = SentenceTransformer(model_name)
            except Exception:
                self.model = None

        # Dimension for all-MiniLM-L6-v2 (or fallback for TF-IDF, which is dynamic)
        self.dimension = 384 if self.model else 512

        os.makedirs(os.path.dirname(index_path), exist_ok=True)

        # Initialize or load FAISS index
        if os.path.exists(f"{index_path}.index"):
            self.index = faiss.read_index(f"{index_path}.index")
            with open(f"{index_path}_metadata.json", "r", encoding="utf-8") as f:
                self.metadata = json.load(f)
        else:
            self.index = faiss.IndexFlatIP(self.dimension)
            self.metadata = []

    def _encode(self, texts: List[str]) -> np.ndarray:
        """Encode texts into vectors using the best available encoder."""
        if self.model is not None:
            return self.model.encode(texts).astype(np.float32)

        # TF-IDF fallback
        if self.tfidf is None:
            self.tfidf = TfidfVectorizer(
                stop_words="english",
                ngram_range=(1, 2),
                max_features=512,
            )
            # Build vocabulary over all stored texts plus new texts
            corpus = [p["text"] for p in self.metadata] + list(texts)
            self.tfidf.fit(corpus)

        vectors = self.tfidf.transform(texts).toarray().astype(np.float32)
        # Normalize for cosine similarity (IP)
        norms = np.linalg.norm(vectors, axis=1, keepdims=True)
        norms[norms == 0] = 1.0
        return vectors / norms

    def add_paper(self, paper_id: str, text: str, metadata: Dict[str, Any]):
        """Add a single paper to the vector database."""
        self.batch_add_papers(
            [{"paper_id": paper_id, "text": text, "metadata": metadata}]
        )

    def search_similar(self, query_text: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """Search for the most similar papers to a query text."""
        if self.index.ntotal == 0:
            return []

        query_embedding = self._encode([query_text])

        top_k = min(top_k, self.index.ntotal)
        scores, indices = self.index.search(query_embedding, top_k)

        results = []
        for score, idx in zip(scores[0], indices[0]):
            if idx != -1 and idx < len(self.metadata):
                info = self.metadata[idx]
                results.append(
                    {
                        "paper_id": info["paper_id"],
                        "similarity_score": float(score),
                        "title": info["metadata"].get("title", ""),
                        "abstract": info["metadata"].get("abstract", ""),
                        "text_snippet": (
                            info["text"][:200] + "..."
                            if len(info["text"]) > 200
                            else info["text"]
                        ),
                    }
                )

        return results

    def batch_add_papers(self, papers: List[Dict[str, Any]]):
        """Add multiple papers to the vector database."""
        if not papers:
            return

        texts = [paper["text"] for paper in papers]

        # Recompute embeddings for all existing + new papers if using TF-IDF
        if self.model is None:
            all_texts = [p["text"] for p in self.metadata] + texts
            self.tfidf = TfidfVectorizer(
                stop_words="english", ngram_range=(1, 2), max_features=512
            )
            self.tfidf.fit(all_texts)
            if self.metadata:
                old_vectors = self._encode([p["text"] for p in self.metadata])
                self.index = faiss.IndexFlatIP(old_vectors.shape[1])
                self.index.add(old_vectors)

        embeddings = self._encode(texts)

        # Rebuild index if dimension changed
        if self.index.d != embeddings.shape[1]:
            self.index = faiss.IndexFlatIP(embeddings.shape[1])
            if self.metadata:
                old_vectors = self._encode([p["text"] for p in self.metadata])
                self.index.add(old_vectors)

        self.index.add(embeddings)

        start_idx = len(self.metadata)
        for i, paper in enumerate(papers):
            self.metadata.append(
                {
                    "paper_id": paper["paper_id"],
                    "text": paper["text"],
                    "metadata": paper["metadata"],
                    "index_position": start_idx + i,
                }
            )

        self._save_index()

    def get_total_papers(self) -> int:
        """Return the number of papers in the database."""
        return len(self.metadata)

    def _save_index(self):
        """Persist the FAISS index and metadata."""
        faiss.write_index(self.index, f"{self.index_path}.index")
        with open(f"{self.index_path}_metadata.json", "w", encoding="utf-8") as f:
            json.dump(self.metadata, f, indent=2)

    def initialize_with_arxiv(self, arxiv_data_path: str, sample_size: int = 1000):
        """Seed the vector database with a sample of the arXiv dataset."""
        import pandas as pd

        if not os.path.exists(arxiv_data_path):
            print("arXiv dataset not found")
            return

        df = pd.read_csv(arxiv_data_path)
        df = df.head(sample_size)

        papers = []
        for _, row in df.iterrows():
            if pd.isna(row["abstract"]) or pd.isna(row["title"]):
                continue
            papers.append(
                {
                    "paper_id": str(row["paper_id"]),
                    "text": f"{row['title']} {row['abstract']}",
                    "metadata": {
                        "title": row["title"],
                        "abstract": row["abstract"],
                        "categories": row.get("categories", []),
                        "authors": row.get("authors", ""),
                    },
                }
            )

        self.batch_add_papers(papers)
        print(f"Initialized vector database with {len(papers)} arXiv papers")


# Lazy singleton instance
_vector_db = None


def get_vector_db() -> "VectorDB":
    """Return a lazily-initialized VectorDB singleton."""
    global _vector_db
    if _vector_db is None:
        _vector_db = VectorDB()
    return _vector_db
