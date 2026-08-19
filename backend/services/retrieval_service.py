import numpy as np
import re
from typing import List, Dict, Any, Optional
from collections import Counter
import math

from services.vector_store import VectorStore
from services.embedding_service import get_embedding_service


class BM25Search:
    """Simple BM25 implementation for keyword-based retrieval."""

    def __init__(self, k1: float = 1.5, b: float = 0.75):
        self.k1 = k1
        self.b = b
        self.doc_lengths: List[int] = []
        self.avg_doc_length: float = 0
        self.doc_freqs: Dict[str, int] = {}
        self.postings: Dict[str, Dict[int, int]] = {}
        self.num_docs: int = 0

    def index(self, documents: List[str]):
        self.doc_lengths = []
        self.doc_freqs = {}
        self.postings = {}
        self.num_docs = len(documents)

        for doc_id, doc in enumerate(documents):
            tokens = self._tokenize(doc)
            self.doc_lengths.append(len(tokens))
            term_counts = Counter(tokens)
            for term, count in term_counts.items():
                if term not in self.postings:
                    self.postings[term] = {}
                self.postings[term][doc_id] = count
                self.doc_freqs[term] = self.doc_freqs.get(term, 0) + 1

        self.avg_doc_length = sum(self.doc_lengths) / max(self.num_docs, 1)

    def search(self, query: str, top_k: int = 10) -> List[Dict[str, Any]]:
        query_tokens = self._tokenize(query)
        scores = [0.0] * self.num_docs

        for term in query_tokens:
            if term not in self.postings:
                continue
            df = self.doc_freqs[term]
            idf = math.log((self.num_docs - df + 0.5) / (df + 0.5) + 1)
            for doc_id, tf in self.postings[term].items():
                dl = self.doc_lengths[doc_id]
                tf_norm = (tf * (self.k1 + 1)) / (tf + self.k1 * (1 - self.b + self.b * dl / max(self.avg_doc_length, 1)))
                scores[doc_id] += idf * tf_norm

        ranked = sorted(range(self.num_docs), key=lambda i: scores[i], reverse=True)
        results = []
        for doc_id in ranked[:top_k]:
            if scores[doc_id] > 0:
                results.append({"doc_id": doc_id, "bm25_score": scores[doc_id]})
        return results

    def _tokenize(self, text: str) -> List[str]:
        return [w.lower() for w in re.findall(r'\b[a-z]{2,}\b', text.lower())]


class HybridRetriever:
    """Combines dense (semantic) retrieval with BM25 keyword retrieval."""

    def __init__(
        self,
        vector_store: VectorStore,
        embedding_service=None,
        semantic_weight: float = 0.65,
        bm25_weight: float = 0.25,
        metadata_weight: float = 0.10,
    ):
        self.vector_store = vector_store
        self.embedding_service = embedding_service or get_embedding_service()
        self.bm25 = BM25Search()
        self.semantic_weight = semantic_weight
        self.bm25_weight = bm25_weight
        self.metadata_weight = metadata_weight
        self.documents: List[Dict[str, Any]] = []
        self._bm25_indexed = False

    def index_chunks(self, chunks: List[Dict[str, Any]]):
        self.documents.extend(chunks)
        texts = [c["content"] for c in chunks]
        if texts:
            embeddings = self.embedding_service.encode(texts)
            self.vector_store.add(embeddings, chunks)
            self.bm25.index(texts)
            self._bm25_indexed = True

    def search(
        self,
        query: str,
        top_k: int = 8,
        filter_paper_id: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        query_embedding = self.embedding_service.encode_query(query)
        semantic_results = self.vector_store.search(query_embedding, top_k=top_k * 2)

        bm25_results = []
        if self._bm25_indexed and self.documents:
            bm25_results_raw = self.bm25.search(query, top_k=top_k * 2)
            doc_id_to_chunk = {}
            for i, doc in enumerate(self.documents):
                doc_id_to_chunk[i] = doc
            for r in bm25_results_raw:
                if r["doc_id"] in doc_id_to_chunk:
                    chunk = doc_id_to_chunk[r["doc_id"]]
                    max_score = max(d["bm25_score"] for d in bm25_results_raw) if bm25_results_raw else 1
                    bm25_results.append({
                        **chunk,
                        "bm25_score_norm": r["bm25_score"] / max(max_score, 1e-10),
                    })

        semantic_scores = {}
        if semantic_results:
            max_sem = max(r["score"] for r in semantic_results) if semantic_results else 1
            for r in semantic_results:
                cid = r.get("chunk_id", "")
                semantic_scores[cid] = r["score"] / max(max_sem, 1e-10)

        bm25_scores = {}
        for r in bm25_results:
            cid = r.get("chunk_id", "")
            bm25_scores[cid] = r.get("bm25_score_norm", 0)

        all_chunks = {}
        for r in semantic_results:
            cid = r.get("chunk_id", "")
            all_chunks[cid] = r
        for r in bm25_results:
            cid = r.get("chunk_id", "")
            if cid not in all_chunks:
                all_chunks[cid] = r

        scored = []
        for cid, chunk in all_chunks.items():
            sem = semantic_scores.get(cid, 0)
            bm = bm25_scores.get(cid, 0)
            meta = self._compute_metadata_score(query, chunk)
            final_score = (
                self.semantic_weight * sem +
                self.bm25_weight * bm +
                self.metadata_weight * meta
            )
            scored.append({**chunk, "final_score": final_score, "semantic_score": sem, "bm25_score": bm})

        scored.sort(key=lambda x: x["final_score"], reverse=True)
        return scored[:top_k]

    def _compute_metadata_score(self, query: str, chunk: Dict[str, Any]) -> float:
        score = 0.0
        section = chunk.get("section_name", "").lower()
        query_lower = query.lower()
        query_words = set(query_lower.split())
        section_words = set(section.split())
        overlap = query_words & section_words
        if overlap:
            score += 0.3
        content = chunk.get("content", "").lower()
        title = chunk.get("title", "").lower()
        for w in query_words:
            if w in content:
                score += 0.05
            if w in title:
                score += 0.1
        return min(score, 1.0)
