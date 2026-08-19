# Architecture

## System Overview

```
                        React Frontend (SPA)
                              |
                              v
                       FastAPI API Layer
                              |
             +----------------+----------------+
             |                |                |
             v                v                v
      Document Pipeline   AI Engine       Analytics
             |                |                |
             v                v                v
        PDF Parser       RAG Pipeline    Trend Engine
        Metadata         Embeddings      Topic Modeling
        Sections         Retrieval       Statistics
        Chunking         Reranking
             |                |
             v                v
        PostgreSQL       FAISS Vector DB
                              |
                              v
                         LLM Provider
```

## Components

### Frontend
- **React 18** with lazy loading and code splitting
- **Tailwind CSS** for styling
- **Recharts** for data visualization
- **Framer Motion** for animations
- **React Context** for state management

### Backend (FastAPI)
- **PDF Parser** - Extracts text, metadata, sections, references
- **Chunking Service** - Section-aware semantic chunking
- **Embedding Service** - Sentence Transformers with TF-IDF fallback
- **Retrieval Service** - Hybrid search (dense + BM25 + metadata)
- **Reranking Service** - Cross-encoder reranking
- **RAG Service** - Full RAG pipeline with citation-backed answers
- **Summarization Service** - Extractive + generative summarization
- **Gap Detection Service** - Structured research gap detection
- **Keyword Extraction Service** - KeyBERT + TF-IDF
- **Recommendation Service** - Semantic similarity-based recommendations
- **Trend Analysis Service** - Research trend analysis

### Database
- PostgreSQL for structured data storage
- FAISS for vector similarity search

## Data Flow

1. **Upload**: PDF -> Parse -> Extract metadata -> Chunk -> Embed -> Store
2. **Query**: Question -> Embed -> Hybrid retrieve -> Rerank -> LLM -> Answer + Citations
3. **Analysis**: Papers -> Extract topics -> Analyze trends -> Generate insights
