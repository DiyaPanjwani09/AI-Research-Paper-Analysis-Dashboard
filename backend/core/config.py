import os
from pathlib import Path
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "AI Research Intelligence Platform"
    environment: str = "development"

    database_url: str = "postgresql://user:password@localhost:5432/research_db"

    upload_dir: str = "uploads"
    max_file_size: int = 50 * 1024 * 1024

    vector_db_path: str = "vector_db/faiss_index"

    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    summarization_model: str = "facebook/bart-large-cnn"
    reranker_model: str = "cross-encoder/ms-marco-MiniLM-L-6-v2"
    llm_provider: str = "openai"
    llm_model: str = "gpt-3.5-turbo"

    chunk_size: int = 700
    chunk_overlap: int = 100
    top_k: int = 8
    rerank_top_k: int = 5

    semantic_weight: float = 0.65
    bm25_weight: float = 0.25
    metadata_weight: float = 0.10

    cors_origins: list = ["http://localhost:3000", "http://127.0.0.1:3000"]

    allowed_origins: str = "http://localhost:3000,http://127.0.0.1:3000"

    class Config:
        env_file = ".env"
        extra = "allow"

    @property
    def cors_origin_list(self) -> list:
        return [o.strip() for o in self.allowed_origins.split(",") if o.strip()]


settings = Settings()
