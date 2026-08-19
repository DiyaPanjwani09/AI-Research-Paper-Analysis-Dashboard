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
- **ML/DL**: Scikit-learn, XGBoost, Sentence Transformers, SciBERT, BERT
- **NLP**: spaCy, NLTK
- **Analytics**: Pandas, NumPy, Plotly
- **Deployment**: Docker, Docker Compose

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
- Docker (optional)

### Installation

```bash
# Clone the repository
git clone <repository-url>
cd research-paper-intelligence-engine

# Run setup script
./setup.sh

# Or manually:

# Backend setup
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: .\venv\Scripts\activate
pip install -r requirements.txt

# Frontend setup
cd ../frontend
npm install

# Preprocess datasets
cd ../datasets
python preprocessing.py

# Initialize vector database
cd ../backend
python -c "from utils.vector_db import vector_db; vector_db.initialize_with_arxiv('../datasets/processed/arxiv_processed.csv')"

# Run the application
# Terminal 1: Start backend
cd backend && python main.py

# Terminal 2: Start frontend
cd frontend && npm start
```

### Using Docker

```bash
docker-compose up --build
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
REDIS_URL=redis://localhost:6379
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
│   ├── app/
│   │   ├── main.py
│   │   └── __init__.py
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
│   ├── utils/
│   │   ├── pdf_parser.py
│   │   ├── summarizer.py
│   │   ├── keyword_extractor.py
│   │   ├── gap_detector.py
│   │   ├── vector_db.py
│   │   ├── rag_chatbot.py
│   │   └── database.py
│   ├── tests/
│   ├── requirements.txt
│   ├── Dockerfile
│   └── .env
│
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   └── Navbar.js
│   │   ├── pages/
│   │   │   ├── Home.js
│   │   │   ├── Upload.js
│   │   │   ├── Summary.js
│   │   │   ├── SimilarPapers.js
│   │   │   ├── Chat.js
│   │   │   └── Analytics.js
│   │   ├── services/
│   │   ├── utils/
│   │   ├── hooks/
│   │   ├── App.js
│   │   ├── index.js
│   │   └── index.css
│   ├── public/
│   ├── package.json
│   ├── tailwind.config.js
│   ├── postcss.config.js
│   ├── nginx.conf
│   └── Dockerfile
│
├── models/
│   ├── summarization/
│   ├── keyword_extraction/
│   ├── similarity/
│   ├── topic_modeling/
│   └── gap_detection/
│
├── datasets/
│   ├── scitldr/
│   ├── arxiv/
│   ├── processed/
│   └── preprocessing.py
│
├── notebooks/
│   ├── README.md
│   ├── data_preprocessing.ipynb
│   ├── summarization_training.ipynb
│   ├── similarity_search.ipynb
│   ├── topic_modeling.ipynb
│   ├── gap_detection.ipynb
│   └── analytics_models.ipynb
│
├── analytics/
│   ├── trend_analysis.py
│   └── topic_modeling.py
│
├── vector_db/
│   └── faiss_index
│
├── uploads/
│
├── requirements.txt
├── README.md
├── docker-compose.yml
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
