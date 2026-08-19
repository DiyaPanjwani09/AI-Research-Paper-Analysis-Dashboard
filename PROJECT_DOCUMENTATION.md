# AI-powered Research Paper Intelligence Engine - Complete Project Documentation

## Overview

A production-ready AI-powered Research Paper Intelligence Engine that enables users to upload research papers and receive intelligent insights including executive summaries, section-wise summaries, research gap detection, similar paper recommendations, research trend analysis, future research suggestions, and a RAG-based chatbot.

## Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │    Backend      │    │   Analytics     │
│   (React)       │◄──►│   (FastAPI)     │◄──►│   Engine       │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                              │                        │
                              ▼                        ▼
                    ┌─────────────────┐    ┌─────────────────┐
                    │   Database     │    │   Vector DB     │
                    │  (PostgreSQL)  │    │    (FAISS)      │
                    └─────────────────┘    └─────────────────┘
```

## Tech Stack

- **Backend**: FastAPI, Python
- **Frontend**: React, Tailwind CSS, Recharts
- **Database**: PostgreSQL
- **Vector Database**: FAISS
- **ML/DL**: Scikit-learn, Transformers, Sentence Transformers
- **NLP**: spaCy, NLTK
- **Analytics**: Pandas, NumPy
- **Deployment**: Render (Web Service + Static Site)

## Features

1. **Smart PDF Upload** - Extract title, authors, abstract, keywords, sections
2. **AI Summarization** - Executive summary, section-wise summaries, key findings
3. **Keyword Extraction** - Technologies, models, datasets, research topics
4. **Research Gap Detection** - Limitations, future work, open problems
5. **Similar Paper Recommendations** - Vector similarity search with FAISS
6. **RAG Chatbot** - Chat with research papers using retrieval-augmented generation
7. **Research Trend Analytics** - Topic frequency, research growth, emerging topics
8. **Topic Modeling** - BERTopic, LDA for topic identification
9. **Future Research Generator** - LLM-based reasoning for research directions
10. **Analytics Dashboard** - Visual insights and metrics

## API Endpoints

### Upload
- `POST /api/v1/upload` - Upload and process research paper PDF

### Summarization
- `POST /api/v1/summarize` - Generate intelligent summaries for research paper

### Keywords
- `POST /api/v1/keywords` - Extract keywords from research paper

### Recommendations
- `POST /api/v1/recommend` - Find similar research papers
- `GET /api/v1/recommend/init` - Initialize recommendation database

### Chat
- `POST /api/v1/chat` - Chat with research paper using RAG
- `GET /api/v1/chat/history` - Get chat conversation history
- `POST /api/v1/chat/clear` - Clear chat conversation history

### Analytics
- `POST /api/v1/analytics/trends` - Analyze research trends
- `GET /api/v1/analytics/visualizations` - Get trend visualizations

## Quick Start

### Prerequisites
- Python 3.11+
- Node.js 18+
- PostgreSQL

### Installation

```bash
# Clone the repository
git clone <repository-url>
cd research-paper-intelligence-engine

# Backend setup
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: .\venv\Scripts\activate
pip install -r ../requirements.txt

# Frontend setup
cd ../frontend
npm install

# Configure environment
cd ../backend
cp .env.example .env

# Run the application
# Terminal 1: Start backend
uvicorn main:app --reload --port 8000

# Terminal 2: Start frontend
cd ../frontend
npm start
```

## Configuration

### Environment Variables

Create a `.env` file in the backend directory:

```bash
cp backend/.env.example backend/.env
```

Edit `backend/.env`:

```
ENVIRONMENT=development
DATABASE_URL=postgresql://user:password@localhost:5432/research_db
```

### Database Setup

```sql
-- Create database
createdb research_db

-- Create user
CREATE USER user WITH PASSWORD 'password';

-- Grant privileges
GRANT ALL PRIVILEGES ON DATABASE research_db TO user;
```

## Project Structure

```
project/
│
├── backend/
│   ├── api/
│   │   ├── routes/
│   │   │   ├── upload.py
│   │   │   ├── summarize.py
│   │   │   ├── keywords.py
│   │   │   ├── recommend.py
│   │   │   ├── chat.py
│   │   │   └── analytics.py
│   │   └── __init__.py
│   ├── core/
│   │   └── config.py
│   ├── models/
│   │   └── database.py
│   ├── schemas/
│   ├── services/
│   │   ├── chunking_service.py
│   │   ├── document_service.py
│   │   ├── embedding_service.py
│   │   ├── gap_detection_service.py
│   │   ├── keyword_service.py
│   │   ├── rag_service.py
│   │   ├── recommendation_service.py
│   │   ├── reranking_service.py
│   │   ├── retrieval_service.py
│   │   ├── summarization_service.py
│   │   ├── trend_service.py
│   │   └── vector_store.py
│   ├── utils/
│   │   ├── pdf_parser.py
│   │   ├── text_utils.py
│   │   └── database.py
│   ├── tests/
│   ├── main.py
│   ├── requirements.txt
│   └── .env
│
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── context/
│   │   ├── pages/
│   │   ├── config.js
│   │   ├── api.js
│   │   ├── App.js
│   │   ├── index.js
│   │   └── index.css
│   ├── public/
│   ├── package.json
│   └── .env
│
├── analytics/
├── datasets/
├── docs/
├── render.yaml
├── requirements.txt
├── README.md
└── setup.sh
```

## Future Improvements

1. **Real LLM Integration** - Integrate with GPT-4, Claude, or open-source LLMs for better summarization
2. **Multi-language Support** - Support for non-English research papers
3. **Collaborative Features** - User accounts, paper sharing, and collaboration
4. **Mobile App** - Native mobile application for iOS and Android
5. **Real-time Updates** - Real-time research trend updates from arXiv
6. **Advanced Analytics** - Citation network analysis, author collaboration graphs
7. **Custom Models** - Fine-tuned domain-specific models for better accuracy
8. **API Rate Limiting** - Production-grade rate limiting and authentication

## License

MIT License

## Contributing

Contributions are welcome! Please open an issue or submit a pull request.
