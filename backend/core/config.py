import os
from pathlib import Path
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "AI Research Intelligence Platform"
    environment: str = "development"
    host: str = "0.0.0.0"
    port: int = int(os.getenv("PORT", "8000"))

    database_url: str = os.getenv("DATABASE_URL", "postgresql://user:password@localhost:5432/research_db")

    upload_dir: str = os.getenv("UPLOAD_DIR", "uploads")
    max_file_size: int = 50 * 1024 * 1024

    vector_db_path: str = os.getenv("VECTOR_DB_PATH", "vector_db")

    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    summarization_model: str = "facebook/bart-large-cnn"
    reranker_model: str = "cross-encoder/ms-marco-MiniLM-L-6-v2"

    chunk_size: int = 700
    chunk_overlap: int = 100
    top_k: int = 8
    rerank_top_k: int = 5

    semantic_weight: float = 0.65
    bm25_weight: float = 0.25
    metadata_weight: float = 0.10

    allowed_origins: str = "http://localhost:3000,http://127.0.0.1:3000"

    class Config:
        env_file = ".env"
        extra = "allow"

    @property
    def cors_origin_list(self) -> list:
        return [o.strip() for o in self.allowed_origins.split(",") if o.strip()]


settings = Settings()
