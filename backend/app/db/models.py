"""
SQLAlchemy ORM models — merefleksikan tabel di migrations/init.sql.
Menggunakan Mapped type annotation (SQLAlchemy 2.0 style).
"""
import uuid
from datetime import datetime
from typing import List, Optional

from sqlalchemy import Float, ForeignKey, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


def _generate_uuid() -> str:
    return str(uuid.uuid4())


class Job(Base):
    """Lowongan kerja hasil scraping."""

    __tablename__ = "jobs"

    id: Mapped[str] = mapped_column(
        String, primary_key=True, default=_generate_uuid
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    company: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    skills: Mapped[list] = mapped_column(JSONB, nullable=False, default=list)
    location: Mapped[Optional[str]] = mapped_column(String(100))
    source_url: Mapped[Optional[str]] = mapped_column(String(500))
    scraped_at: Mapped[datetime] = mapped_column(
        default=func.now(), server_default=func.now()
    )

    # Relasi
    match_logs: Mapped[List["MatchLog"]] = relationship(
        back_populates="job", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Job {self.title} @ {self.company}>"


class CVUpload(Base):
    """CV yang diupload pengguna."""

    __tablename__ = "cv_uploads"

    id: Mapped[str] = mapped_column(
        String, primary_key=True, default=_generate_uuid
    )
    filename: Mapped[str] = mapped_column(String(255), nullable=False)
    storage_path: Mapped[str] = mapped_column(String(500), nullable=False)
    raw_text: Mapped[Optional[str]] = mapped_column(Text)
    skills: Mapped[list] = mapped_column(JSONB, nullable=False, default=list)
    uploaded_at: Mapped[datetime] = mapped_column(
        default=func.now(), server_default=func.now()
    )

    # Relasi
    match_logs: Mapped[List["MatchLog"]] = relationship(
        back_populates="cv", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<CVUpload {self.filename}>"


class MatchLog(Base):
    """Log hasil pencocokan antara CV dan lowongan."""

    __tablename__ = "match_logs"

    id: Mapped[str] = mapped_column(
        String, primary_key=True, default=_generate_uuid
    )
    cv_id: Mapped[str] = mapped_column(
        ForeignKey("cv_uploads.id", ondelete="CASCADE"), nullable=False
    )
    job_id: Mapped[str] = mapped_column(
        ForeignKey("jobs.id", ondelete="CASCADE"), nullable=False
    )
    score: Mapped[float] = mapped_column(Float, nullable=False)
    matched_skills: Mapped[list] = mapped_column(
        JSONB, nullable=False, default=list
    )
    gap_skills: Mapped[list] = mapped_column(
        JSONB, nullable=False, default=list
    )
    matched_at: Mapped[datetime] = mapped_column(
        default=func.now(), server_default=func.now()
    )

    # Relasi
    cv: Mapped["CVUpload"] = relationship(back_populates="match_logs")
    job: Mapped["Job"] = relationship(back_populates="match_logs")

    def __repr__(self) -> str:
        return f"<MatchLog cv={self.cv_id} job={self.job_id} score={self.score:.2f}>"
