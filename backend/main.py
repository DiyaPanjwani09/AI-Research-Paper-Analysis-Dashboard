import os
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import uvicorn

from api.routes import upload, summarize, keywords, recommend, chat, analytics, gaps
from core.config import settings
from utils.database import create_tables

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="AI Research Intelligence Platform",
    description="Production-grade AI-powered research paper analysis and intelligence",
    version="2.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

os.makedirs(settings.upload_dir, exist_ok=True)
os.makedirs(settings.vector_db_path, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=settings.upload_dir), name="uploads")

app.include_router(upload.router, prefix="/api/v1", tags=["upload"])
app.include_router(summarize.router, prefix="/api/v1", tags=["summarization"])
app.include_router(keywords.router, prefix="/api/v1", tags=["keywords"])
app.include_router(recommend.router, prefix="/api/v1", tags=["recommendation"])
app.include_router(chat.router, prefix="/api/v1", tags=["chat"])
app.include_router(analytics.router, prefix="/api/v1", tags=["analytics"])
app.include_router(gaps.router, prefix="/api/v1", tags=["research-gaps"])


@app.on_event("startup")
async def startup_event():
    try:
        create_tables()
        logger.info("Database tables are ready")
    except Exception:
        logger.warning("Database initialization failed; continuing without DB. Non-fatal.")


@app.get("/")
async def root():
    return {
        "message": "AI Research Intelligence Platform API",
        "version": "2.0.0",
        "docs": "/docs",
    }


@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "version": "2.0.0",
        "environment": settings.environment,
    }


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.environment == "development",
    )
