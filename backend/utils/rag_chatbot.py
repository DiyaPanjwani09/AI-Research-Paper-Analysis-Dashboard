import re
from typing import List, Dict
import faiss
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer

try:
    from sentence_transformers import SentenceTransformer
    _HAS_ST = True
except Exception:
    _HAS_ST = False


class RAGChatbot:
    """Retrieval-augmented chatbot for answering questions about a paper."""

    def __init__(self, model_name: str = "sentence-transformers/all-MiniLM-L6-v2"):
        self.model_name = model_name
        self.model = None
        self.tfidf = None

        if _HAS_ST:
            try:
                self.model = SentenceTransformer(model_name)
            except Exception:
                self.model = None

        self.dimension = 384 if self.model else 512
        self.chunk_size = 500
        self.chunk_overlap = 50

        self.paper_chunks = []
        self.faiss_index = None
        self.conversation_history = []

    def index_paper(self, paper_text: str, paper_id: str = None):
        """Chunk and index the paper text for retrieval."""
        self.paper_chunks = []

        chunks = self._chunk_text(paper_text)
        for i, chunk in enumerate(chunks):
            self.paper_chunks.append(
                {
                    "chunk_id": f"{paper_id}_chunk_{i}" if paper_id else f"chunk_{i}",
                    "text": chunk,
                    "position": i,
                }
            )

        if not self.paper_chunks:
            return

        chunk_texts = [c["text"] for c in self.paper_chunks]

        if self.model is not None:
            embeddings = self.model.encode(chunk_texts).astype(np.float32)
        else:
            self.tfidf = TfidfVectorizer(
                stop_words="english", ngram_range=(1, 2), max_features=512
            )
            vectors = self.tfidf.fit_transform(chunk_texts).toarray().astype(np.float32)
            norms = np.linalg.norm(vectors, axis=1, keepdims=True)
            norms[norms == 0] = 1.0
            embeddings = vectors / norms

        self.faiss_index = faiss.IndexFlatIP(embeddings.shape[1])
        self.faiss_index.add(embeddings)

    def query(self, question: str, top_k: int = 3) -> Dict:
        """Answer a question using retrieval from the indexed paper."""
        if not self.faiss_index or len(self.paper_chunks) == 0:
            return {
                "answer": "No paper has been indexed yet. Please upload a paper first.",
                "sources": [],
            }

        # Encode the question
        if self.model is not None:
            query_embedding = self.model.encode([question]).astype(np.float32)
        else:
            query_embedding = self.tfidf.transform([question]).toarray().astype(np.float32)
            norms = np.linalg.norm(query_embedding, axis=1, keepdims=True)
            norms[norms == 0] = 1.0
            query_embedding = query_embedding / norms

        top_k = min(top_k, self.faiss_index.ntotal)
        scores, indices = self.faiss_index.search(query_embedding, top_k)

        relevant_chunks = []
        for score, idx in zip(scores[0], indices[0]):
            if idx != -1 and idx < len(self.paper_chunks):
                chunk = self.paper_chunks[idx]
                relevant_chunks.append(
                    {
                        "text": chunk["text"],
                        "score": float(score),
                        "chunk_id": chunk["chunk_id"],
                    }
                )

        answer = self._generate_answer(question, relevant_chunks)

        self.conversation_history.append(
            {"question": question, "answer": answer, "sources": relevant_chunks}
        )

        return {
            "answer": answer,
            "sources": relevant_chunks,
            "conversation_id": len(self.conversation_history),
        }

    def _chunk_text(self, text: str) -> List[str]:
        """Split text into overlapping chunks of words."""
        words = text.split()
        chunks = []

        i = 0
        while i < len(words):
            chunk = " ".join(words[i : i + self.chunk_size])
            chunks.append(chunk)
            i += self.chunk_size - self.chunk_overlap

        return chunks

    def _generate_answer(self, question: str, relevant_chunks: List[Dict]) -> str:
        """Generate an answer based on retrieved chunks."""
        if not relevant_chunks:
            return "I couldn't find relevant information in the paper to answer this question."

        context = "\n\n".join(chunk["text"] for chunk in relevant_chunks)
        question_lower = question.lower()

        if any(w in question_lower for w in ["dataset", "data set", "data used"]):
            return self._extract_dataset_info(context, question)
        elif any(w in question_lower for w in ["method", "methodology", "approach"]):
            return self._extract_methodology_info(context, question)
        elif any(w in question_lower for w in ["result", "finding", "outcome"]):
            return self._extract_results_info(context, question)
        elif any(w in question_lower for w in ["limitation", "drawback", "weakness"]):
            return self._extract_limitations_info(context, question)
        elif any(w in question_lower for w in ["conclusion", "summary"]):
            return self._extract_conclusion_info(context, question)
        else:
            return f"Based on the paper: {context[:600]}..."

    def _extract_dataset_info(self, context: str, question: str) -> str:
        patterns = [
            r"used (?:the|a) ([A-Za-z0-9\-\s]+) dataset",
            r"dataset (?:named|called) ([A-Za-z0-9\-\s]+)",
            r"([A-Za-z0-9\-\s]+) dataset was used",
            r"data from ([A-Za-z0-9\-\s]+)",
        ]
        datasets = []
        for pattern in patterns:
            datasets.extend(re.findall(pattern, context, re.IGNORECASE))
        if datasets:
            return f"The paper uses the following datasets: {', '.join(list(set(datasets))[:3])}."
        return "The paper doesn't specifically mention the datasets used."

    def _extract_methodology_info(self, context: str, question: str) -> str:
        keywords = ["method", "approach", "technique", "algorithm", "model"]
        sentences = [s.strip() for s in re.split(r"[.!?]+", context)]
        matches = [s for s in sentences if any(k in s.lower() for k in keywords)]
        if matches:
            return f"The methodology involves: {' '.join(matches[:3])}"
        return "The paper's methodology is described in the methods section."

    def _extract_results_info(self, context: str, question: str) -> str:
        patterns = [
            r"results? show(?: that)? ([^.]+)",
            r"we found that ([^.]+)",
            r"the (?:main|key) finding(?: is)? ([^.]+)",
            r"significantly (?:improved|increased|decreased) ([^.]+)",
        ]
        findings = []
        for pattern in patterns:
            findings.extend(re.findall(pattern, context, re.IGNORECASE))
        if findings:
            return f"The key findings are: {' '.join(findings[:3])}"
        return "The paper presents results in the results section."

    def _extract_limitations_info(self, context: str, question: str) -> str:
        keywords = ["limitation", "drawback", "shortcoming", "weakness", "challenge"]
        sentences = [s.strip() for s in re.split(r"[.!?]+", context)]
        matches = [s for s in sentences if any(k in s.lower() for k in keywords)]
        if matches:
            return f"The paper mentions these limitations: {' '.join(matches[:3])}"
        return "The paper doesn't explicitly discuss limitations in this section."

    def _extract_conclusion_info(self, context: str, question: str) -> str:
        keywords = ["conclude", "summary", "overall", "in conclusion", "to summarize"]
        sentences = [s.strip() for s in re.split(r"[.!?]+", context)]
        matches = [s for s in sentences if any(k in s.lower() for k in keywords)]
        if matches:
            return f"The main conclusions are: {' '.join(matches[:3])}"
        return "The paper's conclusions are summarized in the conclusion section."

    def get_conversation_history(self) -> List[Dict]:
        return self.conversation_history

    def clear_conversation(self):
        self.conversation_history = []


# Lazy singleton instance
_rag_chatbot = None


def get_rag_chatbot() -> "RAGChatbot":
    """Return a lazily-initialized RAGChatbot singleton."""
    global _rag_chatbot
    if _rag_chatbot is None:
        _rag_chatbot = RAGChatbot()
    return _rag_chatbot
