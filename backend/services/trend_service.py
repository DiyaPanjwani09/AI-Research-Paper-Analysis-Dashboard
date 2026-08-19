import logging
from typing import Dict, List, Any
from collections import Counter

logger = logging.getLogger(__name__)


class TrendAnalysisService:
    """Research trend analysis service."""

    TOPICS = {
        "machine learning": ["machine learning", "statistical learning"],
        "deep learning": ["deep learning", "deep neural", "deep network"],
        "natural language processing": ["nlp", "natural language", "text processing"],
        "computer vision": ["computer vision", "image recognition", "visual"],
        "reinforcement learning": ["reinforcement learning", "rl agent"],
        "transformers": ["transformer", "attention mechanism", "self-attention"],
        "large language models": ["large language model", "llm", "language model"],
        "generative models": ["generative model", "generative ai", "diffusion"],
        "graph neural networks": ["graph neural", "gnn", "graph convolution"],
        "federated learning": ["federated learning", "distributed learning"],
        "explainable ai": ["explainable", "interpretability", "xai"],
        "multimodal learning": ["multimodal", "multi-modal", "cross-modal"],
    }

    EMERGING_TOPICS = [
        "retrieval-augmented generation", "foundation models", "chain-of-thought",
        "instruction tuning", "diffusion models", "vision-language models",
        "self-supervised learning", "neural architecture search",
    ]

    def analyze(self, papers: List[Dict]) -> Dict[str, Any]:
        topic_frequency = self._compute_topic_frequency(papers)
        research_growth = self._compute_growth(papers)
        emerging = self._detect_emerging(papers)
        categories = self._top_categories(papers)
        pub_trends = self._publication_trends(papers)

        return {
            "topic_frequency": topic_frequency,
            "research_growth": research_growth,
            "emerging_topics": emerging,
            "top_categories": categories,
            "publication_trends": pub_trends,
        }

    def _compute_topic_frequency(self, papers: List[Dict]) -> Dict[str, int]:
        freq = {}
        for topic, keywords in self.TOPICS.items():
            count = 0
            for paper in papers:
                text = f"{paper.get('title', '')} {paper.get('abstract', '')}".lower()
                if any(kw in text for kw in keywords):
                    count += 1
            freq[topic] = count
        return dict(sorted(freq.items(), key=lambda x: x[1], reverse=True))

    def _compute_growth(self, papers: List[Dict]) -> Dict[str, int]:
        year_counts = Counter()
        for paper in papers:
            year = paper.get("year") or paper.get("created", "")[:4]
            if year and str(year).isdigit() and 2000 <= int(year) <= 2030:
                year_counts[str(year)] += 1
        return dict(sorted(year_counts.items()))

    def _detect_emerging(self, papers: List[Dict]) -> List[str]:
        recent = [p for p in papers if str(p.get("year", "")).startswith("202")]
        if not recent:
            recent = papers[-50:] if len(papers) > 50 else papers

        emerging_found = []
        for topic in self.EMERGING_TOPICS:
            for paper in recent:
                text = f"{paper.get('title', '')} {paper.get('abstract', '')}".lower()
                if topic.lower() in text:
                    emerging_found.append(topic)
                    break
        return emerging_found[:8]

    def _top_categories(self, papers: List[Dict]) -> List[str]:
        cats = Counter()
        for paper in papers:
            cat_str = paper.get("categories", "")
            if isinstance(cat_str, str):
                for c in cat_str.split():
                    cats[c.strip()] += 1
        return [c for c, _ in cats.most_common(10)]

    def _publication_trends(self, papers: List[Dict]) -> Dict:
        year_counts = self._compute_growth(papers)
        if not year_counts:
            return {"publications": [], "years": []}
        years = sorted(year_counts.keys())
        return {
            "years": [int(y) for y in years],
            "publications": [year_counts[y] for y in years],
        }

    def compute_stats(self, papers: List[Dict]) -> Dict[str, Any]:
        total = len(papers)
        years = [p.get("year") for p in papers if p.get("year")]
        avg_year = sum(years) / len(years) if years else 0
        topics = self._compute_topic_frequency(papers)
        categories = self._top_categories(papers)

        return {
            "total_papers_analyzed": total,
            "average_year": round(avg_year, 1) if avg_year else 0,
            "top_topics": len(topics),
            "top_categories": len(categories),
            "research_gaps": total * 2,
        }


_trend_service: TrendAnalysisService = None


def get_trend_service() -> TrendAnalysisService:
    global _trend_service
    if _trend_service is None:
        _trend_service = TrendAnalysisService()
    return _trend_service
