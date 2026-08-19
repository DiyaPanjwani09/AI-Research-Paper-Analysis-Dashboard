from sqlalchemy import (
    Column, Integer, String, Text, DateTime, JSON, Float, Boolean,
    ForeignKey, Index, Enum as SAEnum,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
import enum


Base = declarative_base()


def utcnow():
    return datetime.now(timezone.utc)


class PaperStatus(str, enum.Enum):
    UPLOADING = "uploading"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class Paper(Base):
    __tablename__ = "papers"

    id = Column(Integer, primary_key=True, index=True)
    file_id = Column(String, unique=True, index=True, nullable=False)
    title = Column(String, index=True, default="")
    authors = Column(JSON, default=list)
    abstract = Column(Text, default="")
    keywords = Column(JSON, default=list)
    year = Column(Integer, nullable=True)
    venue = Column(String, default="")
    doi = Column(String, nullable=True)
    research_area = Column(String, default="")
    file_path = Column(String, nullable=False)
    full_text = Column(Text, default="")
    status = Column(String, default=PaperStatus.UPLOADING.value)
    word_count = Column(Integer, default=0)
    page_count = Column(Integer, default=0)
    upload_date = Column(DateTime, default=utcnow)
    processing_completed_at = Column(DateTime, nullable=True)

    sections = relationship("PaperSection", back_populates="paper", cascade="all, delete-orphan")
    chunks = relationship("PaperChunk", back_populates="paper", cascade="all, delete-orphan")
    summary = relationship("PaperSummary", back_populates="paper", uselist=False, cascade="all, delete-orphan")
    structured_analysis = relationship("StructuredAnalysis", back_populates="paper", uselist=False, cascade="all, delete-orphan")
    gaps = relationship("ResearchGap", back_populates="paper", cascade="all, delete-orphan")
    conversations = relationship("Conversation", back_populates="paper", cascade="all, delete-orphan")

    __table_args__ = (
        Index("ix_papers_status", "status"),
    )


class PaperSection(Base):
    __tablename__ = "paper_sections"

    id = Column(Integer, primary_key=True, index=True)
    paper_id = Column(Integer, ForeignKey("papers.id", ondelete="CASCADE"), nullable=False)
    section_name = Column(String, nullable=False)
    content = Column(Text, default="")
    page_start = Column(Integer, nullable=True)
    page_end = Column(Integer, nullable=True)
    order_index = Column(Integer, default=0)

    paper = relationship("Paper", back_populates="sections")

    __table_args__ = (
        Index("ix_sections_paper", "paper_id"),
    )


class PaperChunk(Base):
    __tablename__ = "paper_chunks"

    id = Column(Integer, primary_key=True, index=True)
    paper_id = Column(Integer, ForeignKey("papers.id", ondelete="CASCADE"), nullable=False)
    chunk_id = Column(String, unique=True, index=True, nullable=False)
    content = Column(Text, nullable=False)
    section_name = Column(String, default="")
    page_number = Column(Integer, nullable=True)
    position = Column(Integer, default=0)

    paper = relationship("Paper", back_populates="chunks")

    __table_args__ = (
        Index("ix_chunks_paper", "paper_id"),
    )


class PaperSummary(Base):
    __tablename__ = "paper_summaries"

    id = Column(Integer, primary_key=True, index=True)
    paper_id = Column(Integer, ForeignKey("papers.id", ondelete="CASCADE"), unique=True, nullable=False)
    executive_summary = Column(Text, default="")
    section_summaries = Column(JSON, default=dict)
    key_findings = Column(JSON, default=list)
    key_contributions = Column(JSON, default=list)
    generated_at = Column(DateTime, default=utcnow)

    paper = relationship("Paper", back_populates="summary")


class StructuredAnalysis(Base):
    __tablename__ = "structured_analyses"

    id = Column(Integer, primary_key=True, index=True)
    paper_id = Column(Integer, ForeignKey("papers.id", ondelete="CASCADE"), unique=True, nullable=False)
    problem_statement = Column(Text, default="")
    research_objective = Column(Text, default="")
    methodology = Column(Text, default="")
    dataset = Column(Text, default="")
    models = Column(JSON, default=list)
    evaluation_metrics = Column(JSON, default=list)
    key_results = Column(Text, default="")
    contributions = Column(JSON, default=list)
    limitations = Column(JSON, default=list)
    future_work = Column(JSON, default=list)
    generated_at = Column(DateTime, default=utcnow)

    paper = relationship("Paper", back_populates="structured_analysis")


class ResearchGap(Base):
    __tablename__ = "research_gaps"

    id = Column(Integer, primary_key=True, index=True)
    paper_id = Column(Integer, ForeignKey("papers.id", ondelete="CASCADE"), nullable=False)
    gap_text = Column(Text, nullable=False)
    evidence = Column(Text, default="")
    page_number = Column(Integer, nullable=True)
    category = Column(String, default="")
    severity = Column(String, default="Medium")
    confidence = Column(Float, default=0.5)
    gap_type = Column(String, default="limitation")

    paper = relationship("Paper", back_populates="gaps")

    __table_args__ = (
        Index("ix_gaps_paper", "paper_id"),
    )


class Conversation(Base):
    __tablename__ = "conversations"

    id = Column(Integer, primary_key=True, index=True)
    paper_id = Column(Integer, ForeignKey("papers.id", ondelete="CASCADE"), nullable=False)
    session_id = Column(String, unique=True, index=True, nullable=False)
    chat_mode = Column(String, default="researcher")
    created_at = Column(DateTime, default=utcnow)

    paper = relationship("Paper", back_populates="conversations")
    messages = relationship("Message", back_populates="conversation", cascade="all, delete-orphan")


class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(Integer, ForeignKey("conversations.id", ondelete="CASCADE"), nullable=False)
    role = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    sources = Column(JSON, default=list)
    created_at = Column(DateTime, default=utcnow)

    conversation = relationship("Conversation", back_populates="messages")


class Collection(Base):
    __tablename__ = "collections"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(Text, default="")
    created_at = Column(DateTime, default=utcnow)

    papers = relationship("CollectionPaper", back_populates="collection", cascade="all, delete-orphan")


class CollectionPaper(Base):
    __tablename__ = "collection_papers"

    id = Column(Integer, primary_key=True, index=True)
    collection_id = Column(Integer, ForeignKey("collections.id", ondelete="CASCADE"), nullable=False)
    paper_id = Column(Integer, ForeignKey("papers.id", ondelete="CASCADE"), nullable=False)
    added_at = Column(DateTime, default=utcnow)

    collection = relationship("Collection", back_populates="papers")


class Experiment(Base):
    __tablename__ = "experiments"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    embedding_model = Column(String, default="")
    chunk_size = Column(Integer, default=700)
    chunk_overlap = Column(Integer, default=100)
    top_k = Column(Integer, default=8)
    reranker_model = Column(String, default="")
    results = Column(JSON, default=dict)
    metrics = Column(JSON, default=dict)
    notes = Column(Text, default="")
    created_at = Column(DateTime, default=utcnow)


class KnowledgeGraphEdge(Base):
    __tablename__ = "knowledge_graph_edges"

    id = Column(Integer, primary_key=True, index=True)
    source_type = Column(String, nullable=False)
    source_id = Column(String, nullable=False)
    target_type = Column(String, nullable=False)
    target_id = Column(String, nullable=False)
    relation = Column(String, nullable=False)
    metadata = Column(JSON, default=dict)

    __table_args__ = (
        Index("ix_kg_source", "source_type", "source_id"),
        Index("ix_kg_target", "target_type", "target_id"),
    )
