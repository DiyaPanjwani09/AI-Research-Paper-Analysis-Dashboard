# AI Research Intelligence Platform

A production-grade AI-powered research paper analysis and intelligence platform.

## Features

- **Smart PDF Upload** - Automatic metadata extraction (title, authors, abstract, year, venue, DOI)
- **Hierarchical Summarization** - Executive summaries, section-wise breakdowns, key findings & contributions
- **Citation-Backed RAG** - Ask questions and get answers with page-level citations
- **Hybrid Retrieval** - Dense (semantic) + BM25 (keyword) + metadata scoring
- **Cross-Encoder Reranking** - Improves retrieval quality with cross-encoder models
- **Multi-Mode Chat** - Researcher, Student, Beginner, Executive explanation modes
- **Semantic Paper Search** - Find similar papers with explanation
- **Research Gap Detection** - Structured gaps with categories, severity, and confidence
- **Keyword Extraction** - Technologies, models, datasets, and research topics
- **Research Trend Analytics** - Topic frequency, growth, emerging topics, publication trends

## Tech Stack

| Component | Technology |
|-----------|-----------|
| Frontend | React 18, Tailwind CSS, Recharts |
| Backend | FastAPI, Python 3.11 |
| Database | PostgreSQL |
| Vector DB | FAISS |
| Embeddings | Sentence Transformers |
| Reranker | Cross-Encoder |

## Project Structure

```
├── backend/
│   ├── api/routes/          # FastAPI route handlers
│   ├── core/                # Configuration
│   ├── models/              # Database models
│   ├── schemas/             # API schemas
│   ├── services/            # Business logic (ML/NLP services)
│   ├── tests/               # Tests
│   ├── utils/               # PDF parser, helpers
│   ├── requirements.txt     # Backend dependencies
│   └── main.py              # FastAPI application
├── frontend/
│   ├── src/                 # React source
│   ├── public/              # Static assets
│   └── package.json         # Frontend dependencies
├── analytics/               # Trend analysis modules
├── datasets/                # Dataset preprocessing
├── docs/                    # Documentation
├── render.yaml              # Render Blueprint
└── .env.example             # Environment variables
```

## Local Development

### Prerequisites
- Python 3.11+
- Node.js 18+
- PostgreSQL

### Backend

```bash
cd backend
python -m venv venv

# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate

pip install -r ../requirements.txt

# Copy .env and configure
cp .env.example .env

# Run locally
uvicorn main:app --reload --port 8000
```

Backend API: http://localhost:8000
API Docs: http://localhost:8000/docs

### Frontend

```bash
cd frontend

# Create .env
echo "REACT_APP_API_URL=http://localhost:8000" > .env

npm install
npm start
```

Frontend: http://localhost:3000

## Environment Variables

### Backend (.env)

Copy `.env.example` to `.env` in the `backend/` directory.

| Variable | Default | Description |
|----------|---------|-------------|
| `DATABASE_URL` | - | PostgreSQL connection string |
| `EMBEDDING_MODEL` | `sentence-transformers/all-MiniLM-L6-v2` | Embedding model |
| `RERANKER_MODEL` | `cross-encoder/ms-marco-MiniLM-L-6-v2` | Reranker model |
| `CHUNK_SIZE` | `700` | Words per chunk |
| `TOP_K` | `8` | Initial retrieval depth |
| `RERANK_TOP_K` | `5` | Final results after reranking |
| `SEMANTIC_WEIGHT` | `0.65` | Dense retrieval weight |
| `BM25_WEIGHT` | `0.25` | Keyword retrieval weight |
| `METADATA_WEIGHT` | `0.10` | Metadata score weight |
| `ALLOWED_ORIGINS` | `http://localhost:3000` | CORS origins |
| `MAX_FILE_SIZE` | `52428800` | Max upload size (bytes) |
| `UPLOAD_DIR` | `uploads` | Upload directory |
| `VECTOR_DB_PATH` | `vector_db` | FAISS index directory |

### Frontend (.env)

| Variable | Default | Description |
|----------|---------|-------------|
| `REACT_APP_API_URL` | `http://localhost:8000` | Backend API URL |

## Render Deployment

The repository includes a production-ready `render.yaml` Blueprint. Use **Render > New > Blueprint**, select this GitHub repository, and apply the detected Blueprint.

The Blueprint creates:

- `ai-research-backend`: FastAPI service with `/health` checks
- `ai-research-frontend`: React static site with SPA rewrites
- `ai-research-db`: Render Postgres database

The frontend API URL and backend CORS origin are wired automatically from Render's generated service URLs, so you do not need to hardcode `*.onrender.com` URLs manually.

See `RENDER_DEPLOY.md` for the step-by-step checklist and free-plan limitations.

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/upload` | Upload PDF |
| POST | `/api/v1/chat` | RAG Q&A |
| POST | `/api/v1/summarize` | Generate summaries |
| POST | `/api/v1/keywords` | Extract keywords |
| POST | `/api/v1/gaps` | Detect research gaps |
| POST | `/api/v1/recommend` | Find similar papers |
| POST | `/api/v1/search` | Semantic search |
| POST | `/api/v1/analytics/trends` | Analyze trends |
| GET | `/api/v1/analytics/stats` | Statistics |
| GET | `/health` | Health check |

## Limitations

- **FAISS storage is local**: Vector indexes are stored on the local filesystem and are not persistent across Render redeployments (free plan scales to 0). Suitable for demos and development.
- **PDF uploads are local**: Uploaded PDFs are stored on the server and may not persist across restarts.
- **ML model loading**: First request may take extra time to download model weights.

## License

MIT License
