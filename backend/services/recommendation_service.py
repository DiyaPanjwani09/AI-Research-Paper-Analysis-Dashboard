import os
import logging
from typing import Dict, List, Any

logger = logging.getLogger(__name__)

_ARXIV_DATA = [
    {"paper_id": "arxiv_001", "title": "Attention Is All You Need", "abstract": "The dominant sequence transduction models are based on complex recurrent or convolutional neural networks. We propose a new simple network architecture, the Transformer, based solely on attention mechanisms.", "authors": "Vaswani et al.", "categories": "cs.CL cs.LG", "created": "2017-06-12"},
    {"paper_id": "arxiv_002", "title": "BERT: Pre-training of Deep Bidirectional Transformers", "abstract": "We introduce a new language representation model called BERT, which stands for Bidirectional Encoder Representations from Transformers. BERT is designed to pre-train deep bidirectional representations.", "authors": "Devlin et al.", "categories": "cs.CL cs.AI", "created": "2018-10-11"},
    {"paper_id": "arxiv_003", "title": "Language Models are Few-Shot Learners", "abstract": "Recent work has demonstrated substantial gains on many NLP tasks by pre-training on a large corpus of text followed by fine-tuning on a specific task. GPT-3 achieves strong performance on many NLP benchmarks.", "authors": "Brown et al.", "categories": "cs.CL cs.LG", "created": "2020-05-28"},
    {"paper_id": "arxiv_004", "title": "Deep Residual Learning for Image Recognition", "abstract": "Deeper neural networks are more difficult to train. We present a residual learning framework to ease the training of networks that are substantially deeper than those used previously.", "authors": "He et al.", "categories": "cs.CV cs.AI", "created": "2015-12-10"},
    {"paper_id": "arxiv_005", "title": "Generative Adversarial Networks", "abstract": "We propose a new framework for estimating generative models via an adversarial process, in which we simultaneously train two models: a generative model G and a discriminative model D.", "authors": "Goodfellow et al.", "categories": "cs.LG stat.ML", "created": "2014-06-10"},
    {"paper_id": "arxiv_006", "title": "Dropout: A Simple Way to Prevent Neural Networks from Overfitting", "abstract": "Deep neural nets with a large number of parameters are very powerful machine learning systems. Overfitting is a serious problem in such networks. Dropout is a technique for addressing this problem.", "authors": "Srivastava et al.", "categories": "cs.LG stat.ML", "created": "2014-06-14"},
    {"paper_id": "arxiv_007", "title": "Adam: A Method for Stochastic Optimization", "abstract": "We introduce Adam, an algorithm for first-order gradient-based optimization of stochastic objective functions, based on adaptive estimates of lower-order moments.", "authors": "Kingma et al.", "categories": "cs.LG stat.ML", "created": "2014-12-22"},
    {"paper_id": "arxiv_008", "title": "Batch Normalization", "abstract": "Training Deep Neural Networks is complicated by the fact that the distribution of each layer's inputs changes during training, as the parameters of the previous layers change. We refer to this phenomenon as internal covariate shift.", "authors": "Ioffe et al.", "categories": "cs.LG stat.ML", "created": "2015-02-11"},
    {"paper_id": "arxiv_009", "title": "ImageNet Classification with Deep Convolutional Neural Networks", "abstract": "We trained a large, deep convolutional neural network to classify the 1.2 million high-resolution images in the ImageNet LSVRC-2010 contest into the 1000 different classes.", "authors": "Krizhevsky et al.", "categories": "cs.CV cs.AI", "created": "2012-09-30"},
    {"paper_id": "arxiv_010", "title": "Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks", "abstract": "Large pre-trained language models store factual knowledge in their parameters and achieve state-of-the-art when fine-tuned. We explore a general-purpose fine-free retrieval-augmented generation (RAG) architecture.", "authors": "Lewis et al.", "categories": "cs.CL cs.IR", "created": "2020-05-22"},
    {"paper_id": "arxiv_011", "title": "ViT: An Image is Worth 16x16 Words", "abstract": "While the Transformer architecture has become the de-facto standard for natural language processing tasks, its applications to computer vision remain limited. We show that a pure transformer applied directly to sequences of image patches can perform very well on image classification.", "authors": "Dosovitskiy et al.", "categories": "cs.CV cs.LG", "created": "2020-10-22"},
    {"paper_id": "arxiv_012", "title": "Neural Architecture Search with Reinforcement Learning", "abstract": "Neural network design is a challenging problem. We propose using a recurrent network to generate the model descriptions of neural networks and train this RNN with reinforcement learning to maximize the expected accuracy.", "authors": "Zoph et al.", "categories": "cs.LG cs.NE", "created": "2016-11-04"},
    {"paper_id": "arxiv_013", "title": "GPT-4 Technical Report", "abstract": "We report the development of GPT-4, a large-scale, multimodal model which can accept image and text inputs and produce text outputs. GPT-4 exhibits human-level performance on various benchmarks.", "authors": "OpenAI", "categories": "cs.CL cs.AI", "created": "2023-03-15"},
    {"paper_id": "arxiv_014", "title": "EfficientNet: Rethinking Model Scaling for CNNs", "abstract": "Scaling up convolutional neural networks has been important for achieving higher accuracy. We propose a compound scaling method that uniformly scales all dimensions of depth, width, and resolution.", "authors": "Tan et al.", "categories": "cs.CV cs.LG", "created": "2019-05-28"},
    {"paper_id": "arxiv_015", "title": "Federated Learning of Deep Networks Using Model Averaging", "abstract": "The mobile devices of today's users contain a wealth of data that can be used to improve the user experience. We present a practical method for distributed training across mobile devices.", "authors": "McMahan et al.", "categories": "cs.LG stat.ML", "created": "2017-02-15"},
]


class RecommendationService:
    """Paper recommendation service using embedding similarity."""

    def __init__(self):
        self.papers = _ARXIV_DATA

    def get_recommendations(
        self, paper_text: str, top_k: int = 5
    ) -> List[Dict[str, Any]]:
        from services.embedding_service import get_embedding_service
        embedding_service = get_embedding_service()

        query_emb = embedding_service.encode([paper_text[:2000]])
        paper_texts = [f"{p['title']} {p['abstract']}" for p in self.papers]
        paper_embs = embedding_service.encode(paper_texts)

        import numpy as np
        query_norm = query_emb / (np.linalg.norm(query_emb, axis=1, keepdims=True) + 1e-10)
        paper_norm = paper_embs / (np.linalg.norm(paper_embs, axis=1, keepdims=True) + 1e-10)
        similarities = (paper_norm @ query_norm.T).flatten()

        top_indices = similarities.argsort()[::-1][:top_k]
        results = []
        for idx in top_indices:
            paper = self.papers[idx]
            score = float(similarities[idx])
            reasons = self._generate_reasons(paper_text, paper)
            results.append({
                "paper_id": paper["paper_id"],
                "title": paper["title"],
                "abstract": paper["abstract"],
                "authors": paper["authors"],
                "similarity_score": score,
                "reasons": reasons,
            })
        return results

    def _generate_reasons(self, query_text: str, paper: Dict) -> List[str]:
        reasons = []
        query_lower = query_text.lower()
        title_lower = paper["title"].lower()
        abstract_lower = paper["abstract"].lower()

        query_words = set(query_lower.split())
        title_words = set(title_lower.split())
        if len(query_words & title_words) > 2:
            reasons.append("Similar research problem")

        method_words = {"transformer", "attention", "cnn", "rnn", "lstm", "gan", "vae", "bert", "gpt"}
        q_methods = query_words & method_words
        p_methods = title_words | set(abstract_lower.split()) & method_words
        if q_methods & p_methods:
            reasons.append("Similar methodology")

        if any(d in abstract_lower for d in ["dataset", "benchmark", "evaluation"]):
            reasons.append("Similar evaluation approach")

        if not reasons:
            reasons.append("Semantically similar content")

        return reasons
