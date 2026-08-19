# RAG Pipeline

## Overview

The RAG pipeline provides citation-backed answers from research papers.

## Pipeline

```
User Question -> Hybrid Retrieve -> Rerank -> Answer + Citations
```

## Configuration

Set via environment variables: EMBEDDING_MODEL, RERANKER_MODEL, CHUNK_SIZE, TOP_K, etc.

## Citation Format

Each answer includes source citations with page numbers and section info.
