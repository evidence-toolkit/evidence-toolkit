"""Database models and helpers for the evidence toolkit."""

from __future__ import annotations

import datetime as dt
from pathlib import Path
from typing import Optional

from sqlalchemy import (
    JSON,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
    create_engine,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship, sessionmaker


class Base(DeclarativeBase):
    pass


class Evidence(Base):
    __tablename__ = "evidence"

    sha256: Mapped[str] = mapped_column(String(64), primary_key=True)
    case_id: Mapped[Optional[str]] = mapped_column(String, index=True)
    original_ext: Mapped[Optional[str]] = mapped_column(String(10))
    original_bytes: Mapped[int] = mapped_column(Integer)
    phash: Mapped[Optional[str]] = mapped_column(String(32))
    exif_json: Mapped[Optional[dict]] = mapped_column(JSON)
    added_at: Mapped[dt.datetime] = mapped_column(DateTime, default=dt.datetime.utcnow)
    path: Mapped[str] = mapped_column(Text, unique=True)

    analyses: Mapped[list["Analysis"]] = relationship(
        back_populates="evidence", cascade="all, delete-orphan"
    )


class Analysis(Base):
    __tablename__ = "analysis"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    sha256: Mapped[str] = mapped_column(String(64), ForeignKey("evidence.sha256"))
    created_at: Mapped[dt.datetime] = mapped_column(DateTime, default=dt.datetime.utcnow)
    model: Mapped[str] = mapped_column(String)
    model_revision: Mapped[Optional[str]] = mapped_column(String)
    prompt: Mapped[str] = mapped_column(Text)
    prompt_hash: Mapped[str] = mapped_column(String(64))
    response_raw: Mapped[dict] = mapped_column(JSON)
    analysis_json: Mapped[dict] = mapped_column(JSON)
    tokens_input: Mapped[Optional[int]] = mapped_column(Integer)
    tokens_output: Mapped[Optional[int]] = mapped_column(Integer)
    temperature: Mapped[Optional[float]] = mapped_column(Float)

    evidence: Mapped[Evidence] = relationship(back_populates="analyses")

    __table_args__ = (
        UniqueConstraint("sha256", "prompt_hash", name="uniq_analysis"),
    )


def get_engine(path: Path):
    """Create a SQLite engine bound to *path* (file is created if necessary)."""

    return create_engine(f"sqlite:///{path}", future=True)


def init_session_factory(path: Path):
    """Return a session factory bound to the SQLite database."""

    engine = get_engine(path)
    Base.metadata.create_all(engine)
    return sessionmaker(bind=engine, future=True)


__all__ = ["Base", "Evidence", "Analysis", "get_engine", "init_session_factory"]
