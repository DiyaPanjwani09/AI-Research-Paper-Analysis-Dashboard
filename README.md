# AI Research Intelligence Platform

Production-grade AI-powered research paper analysis and intelligence platform.

## Features

- Smart PDF upload with metadata extraction
- Hierarchical summarization (executive + section summaries)
- Citation-backed RAG chatbot with hybrid retrieval
- Cross-encoder reranking for improved answer quality
- Multi-mode chat (Researcher/Student/Beginner/Executive)
- Semantic paper search and recommendations
- Structured research gap detection with severity scoring
- Research trend analytics and visualization

## Quick Start

```bash
# Docker
cp .env.example .env
docker compose up --build

# Frontend: http://localhost:3000
# Backend API: http://localhost:8000
# API Docs: http://localhost:8000/docs
```

## Tech Stack

- **Frontend**: React 18, Tailwind CSS, Recharts, Framer Motion
- **Backend**: FastAPI, Python 3.11
- **Database**: PostgreSQL 15, FAISS
- **ML/NLP**: Sentence Transformers, Cross-Encoder, spaCy, KeyBERT

## Architecture

```
React Frontend -> FastAPI -> Document Pipeline -> PDF Parser
                                  |                   |
                                  v                   v
                            AI Engine            Analytics
                                  |                   |
                                  v                   v
                         FAISS + PostgreSQL     Insights
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/upload` | Upload PDF |
| POST | `/api/v1/chat` | RAG Q&A |
| POST | `/api/v1/summarize` | Summaries |
| POST | `/api/v1/keywords` | Keywords |
| POST | `/api/v1/gaps` | Research gaps |
| POST | `/api/v1/recommend` | Similar papers |
| POST | `/api/v1/search` | Semantic search |
| POST | `/api/v1/analytics/trends` | Trends |

## License

MIT
