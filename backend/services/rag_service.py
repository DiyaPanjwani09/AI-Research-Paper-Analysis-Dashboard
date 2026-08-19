import logging
from typing import List, Dict, Any, Optional

from services.embedding_service import get_embedding_service
from services.vector_store import VectorStore
from services.chunking_service import SemanticChunker, Chunk
from services.retrieval_service import HybridRetriever
from services.reranking_service import RerankerService
from core.config import settings

logger = logging.getLogger(__name__)


class RAGService:
    """Retrieval-Augmented Generation service with hybrid search and reranking."""

    def __init__(self):
        self.embedding_service = get_embedding_service(settings.embedding_model)
        self.vector_store = VectorStore(dimension=384)
        self.chunker = SemanticChunker(
            chunk_size=settings.chunk_size,
            chunk_overlap=settings.chunk_overlap,
        )
        self.retriever = HybridRetriever(
            vector_store=self.vector_store,
            embedding_service=self.embedding_service,
            semantic_weight=settings.semantic_weight,
            bm25_weight=settings.bm25_weight,
            metadata_weight=settings.metadata_weight,
        )
        self.reranker = RerankerService(settings.reranker_model)
        self._indexed_documents: Dict[str, List[Chunk]] = {}

    def index_paper(
        self,
        document_id: str,
        full_text: str,
        sections: Dict[str, str],
        title: str = "",
        metadata: Optional[Dict] = None,
    ) -> int:
        chunks = self.chunker.chunk_paper(
            document_id=document_id,
            full_text=full_text,
            sections=sections,
        )

        chunk_dicts = []
        for chunk in chunks:
            d = chunk.to_dict()
            d["title"] = title
            if metadata:
                d.update(metadata)
            chunk_dicts.append(d)

        self.retriever.index_chunks(chunk_dicts)
        self._indexed_documents[document_id] = chunks

        logger.info(f"Indexed {len(chunks)} chunks for document {document_id}")
        return len(chunks)

    def query(
        self,
        question: str,
        top_k: int = 8,
        rerank_top_k: int = 5,
        filter_paper_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        if self.vector_store.size == 0:
            return {
                "answer": "No documents have been indexed yet. Please upload a paper first.",
                "sources": [],
                "retrieval_time": 0,
            }

        import time
        start = time.time()

        retrieval_results = self.retriever.search(
            query=question,
            top_k=top_k,
            filter_paper_id=filter_paper_id,
        )

        retrieval_time = time.time() - start

        rerank_start = time.time()
        reranked = self.reranker.rerank(
            query=question,
            results=retrieval_results,
            top_k=rerank_top_k,
        )
        rerank_time = time.time() - rerank_start

        sources = []
        for r in reranked:
            sources.append({
                "chunk_id": r.get("chunk_id", ""),
                "content": r.get("content", ""),
                "section": r.get("section_name", ""),
                "page": r.get("page_number"),
                "document_id": r.get("document_id", ""),
                "score": r.get("rerank_score", r.get("final_score", 0)),
            })

        context = "\n\n---\n\n".join([s["content"] for s in sources])
        answer = self._format_answer(question, context, sources)

        total_time = time.time() - start

        return {
            "answer": answer,
            "sources": sources,
            "context": context,
            "retrieval_time": retrieval_time,
            "rerank_time": rerank_time,
            "total_time": total_time,
        }

    def _format_answer(
        self,
        question: str,
        context: str,
        sources: List[Dict],
    ) -> str:
        if not context.strip():
            return "I couldn't find sufficient evidence in the uploaded paper to answer this question."

        context_lower = context.lower()
        question_lower = question.lower()

        relevant_sentences = []
        for sentence in context.split('.'):
            sentence = sentence.strip()
            if len(sentence) < 20:
                continue
            question_words = [w for w in question_lower.split() if len(w) > 3]
            if any(w in sentence.lower() for w in question_words):
                relevant_sentences.append(sentence)

        if relevant_sentences:
            answer = ". ".join(relevant_sentences[:5]) + "."
        else:
            paragraphs = [p.strip() for p in context.split('\n\n') if p.strip()]
            if paragraphs:
                answer = paragraphs[0]
            else:
                answer = context[:1000]

        citation_markers = []
        for i, source in enumerate(sources[:3]):
            page_info = f"Page {source['page']}" if source.get('page') else ""
            section_info = source.get('section', '')
            citation_markers.append(f"[{i + 1}] {section_info} {page_info}".strip())

        if citation_markers:
            answer += "\n\nSources: " + "; ".join(citation_markers)

        return answer


_rag_service: Optional[RAGService] = None


def get_rag_service() -> RAGService:
    global _rag_service
    if _rag_service is None:
        _rag_service = RAGService()
    return _rag_service
