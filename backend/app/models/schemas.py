"""
Pydantic schemas — mendefinisikan bentuk request & response JSON.
Dipisahkan dari ORM model agar bisa berevolusi independen.
"""
from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


# ═══════════════════════════════════════════════════════════════
# Jobs
# ═══════════════════════════════════════════════════════════════

class JobBase(BaseModel):
    title: str
    company: str
    description: str
    skills: List[str] = []
    location: Optional[str] = None
    source_url: Optional[str] = None


class JobCreate(JobBase):
    """Payload untuk menambah lowongan baru."""
    pass


class JobResponse(JobBase):
    """Response satu lowongan."""
    id: str
    scraped_at: datetime

    model_config = {"from_attributes": True}


class JobListResponse(BaseModel):
    """Response paginated daftar lowongan."""
    total: int
    page: int
    per_page: int
    data: List[JobResponse]


# ═══════════════════════════════════════════════════════════════
# CV Upload
# ═══════════════════════════════════════════════════════════════

class CVUploadResponse(BaseModel):
    """Response setelah upload CV berhasil."""
    id: str
    filename: str
    storage_path: str
    skills: List[str]
    uploaded_at: datetime

    model_config = {"from_attributes": True}


# ═══════════════════════════════════════════════════════════════
# Matching
# ═══════════════════════════════════════════════════════════════

class MatchRequest(BaseModel):
    """Request untuk mencocokkan CV dengan lowongan."""
    cv_id: str
    top_k: int = Field(default=10, ge=1, le=50, description="Jumlah top lowongan yang dikembalikan")


class MatchResultItem(BaseModel):
    """Satu item hasil pencocokan."""
    job_id: str
    title: str
    company: str
    score: float = Field(ge=0, le=1)
    matched_skills: List[str]
    gap_skills: List[str]


class MatchResponse(BaseModel):
    """Response lengkap hasil matching."""
    cv_id: str
    results: List[MatchResultItem]


# ═══════════════════════════════════════════════════════════════
# Trends (dari ML Service)
# ═══════════════════════════════════════════════════════════════

class TrendItem(BaseModel):
    """Satu prediksi tren skill."""
    skill: str
    current_demand: float
    predicted_demand: float
    growth_pct: float


class TrendResponse(BaseModel):
    """Response prediksi tren skill."""
    period: str
    trends: List[TrendItem]
