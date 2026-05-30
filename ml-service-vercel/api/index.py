"""
SkillScout Nusantara — ML Service (Vercel Serverless)
Platform: Vercel (Python Serverless Functions)

Versi ringan tanpa TensorFlow — menggunakan TF-IDF + Cosine Similarity
sebagai primary matcher karena Vercel memiliki batas 250MB deployment size
(TensorFlow ~500MB+ tidak muat).

Endpoints:
  1. POST /rank       → ranking lowongan berdasarkan kecocokan CV
  2. GET  /trends     → prediksi tren skill (data statis)
  3. GET  /health     → health check
  4. GET  /model-info → info arsitektur & konfigurasi

API contract 100% kompatibel dengan ml-service (Railway version).
"""

import os
import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

# ── Logging ──────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger("ml-service-vercel")

# ── Skill Normalization (konsisten dengan ai/model.ipynb) ────
NORMALIZE = {
    "power bi": "powerbi",
    "machine learning": "machinelearning",
    "deep learning": "deeplearning",
    "natural language processing": "nlp",
    "data analysis": "dataanalysis",
    "data analytics": "dataanalytics",
    "data science": "datascience",
    "data engineering": "dataengineering",
    "computer vision": "computervision",
    "neural network": "neuralnetwork",
    "big data": "bigdata",
    "project management": "projectmanagement",
    "time series": "timeseries",
    "scikit learn": "scikitlearn",
    "google analytics": "googleanalytics",
    "looker studio": "lookerstudio",
}


def normalize_skills(text: str) -> str:
    """
    Normalisasi multi-word skills menjadi single token.
    Harus IDENTIK dengan fungsi di ai/model.ipynb agar
    tokenizer menghasilkan sequence yang konsisten.
    """
    t = str(text).lower()
    for phrase, token in NORMALIZE.items():
        t = t.replace(phrase, token)
    return t


# ── FastAPI app ──────────────────────────────────────────────
app = FastAPI(
    title="SkillScout ML Service (Vercel)",
    description=(
        "TF-IDF + Cosine Similarity untuk job-CV matching.\n\n"
        "**Platform:** Vercel Serverless Functions\n\n"
        "**Catatan:** Versi ini menggunakan TF-IDF karena TensorFlow "
        "terlalu besar untuk Vercel (>250MB limit). "
        "Untuk deep learning inference, gunakan versi Railway."
    ),
    version="2.0.0-vercel",
)

# ── CORS ─────────────────────────────────────────────────────
_origins = os.getenv("ALLOWED_ORIGINS", "*")
app.add_middleware(
    CORSMiddleware,
    allow_origins=_origins.split(",") if _origins != "*" else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ══════════════════════════════════════════════════════════════
# Schemas (identik dengan ml-service Railway)
# ══════════════════════════════════════════════════════════════

class JobPayload(BaseModel):
    id: str
    title: str = ""
    company: str = ""
    description: str = ""
    skills: list[str] = []


class RankRequest(BaseModel):
    cv_text: str = Field(..., min_length=10, description="Teks CV mentah")
    jobs: list[JobPayload] = Field(
        ..., min_length=1, description="Daftar lowongan"
    )
    top_k: int = Field(default=10, ge=1, le=50)


class MatchResult(BaseModel):
    job_id: str
    title: str
    company: str
    score: float
    matched_skills: list[str]
    gap_skills: list[str]


class RankResponse(BaseModel):
    results: list[MatchResult]
    model_used: str = "tfidf_vercel"


class TrendItem(BaseModel):
    skill: str
    current_demand: float
    predicted_demand: float
    growth_pct: float


class TrendResponse(BaseModel):
    period: str
    trends: list[TrendItem]


# ══════════════════════════════════════════════════════════════
# Helper functions
# ══════════════════════════════════════════════════════════════

def compute_skill_match(
    cv_text: str, job_skills: list[str]
) -> tuple[list[str], list[str]]:
    """Hitung matched skills dan gap skills."""
    cv_lower = cv_text.lower()
    job_skill_set = set(s.lower() for s in job_skills)
    matched = sorted(s for s in job_skill_set if s in cv_lower)
    gap = sorted(s for s in job_skill_set if s not in cv_lower)
    return matched, gap


def tfidf_rank(
    cv_text: str, jobs: list[JobPayload], top_k: int
) -> list[dict]:
    """
    TF-IDF + Cosine Similarity + Skill Overlap scoring.

    Scoring formula:
      combined = 0.6 × TF-IDF cosine similarity
               + 0.4 × skill overlap ratio
    """
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity

    # Normalize skills di CV dan job texts
    cv_normalized = normalize_skills(cv_text)
    job_texts = [
        normalize_skills(f"{j.title} {j.description} {' '.join(j.skills)}")
        for j in jobs
    ]
    corpus = [cv_normalized] + job_texts

    vectorizer = TfidfVectorizer(
        max_features=5000, stop_words="english", ngram_range=(1, 2)
    )
    tfidf = vectorizer.fit_transform(corpus)
    similarities = cosine_similarity(tfidf[0:1], tfidf[1:]).flatten()

    results = []
    for idx, job in enumerate(jobs):
        matched, gap = compute_skill_match(cv_text, job.skills)
        skill_score = len(matched) / max(
            len(set(s.lower() for s in job.skills)), 1
        )
        combined = 0.6 * similarities[idx] + 0.4 * skill_score

        results.append(
            {
                "job_id": job.id,
                "title": job.title,
                "company": job.company,
                "score": round(float(combined), 4),
                "matched_skills": matched,
                "gap_skills": gap,
            }
        )

    results.sort(key=lambda x: x["score"], reverse=True)
    return results[:top_k]


# ══════════════════════════════════════════════════════════════
# Endpoints
# ══════════════════════════════════════════════════════════════

@app.post("/rank", response_model=RankResponse)
async def rank_jobs_endpoint(req: RankRequest):
    """
    Ranking lowongan berdasarkan kecocokan dengan CV.
    Menggunakan TF-IDF + Cosine Similarity + Skill Overlap.
    """
    results = tfidf_rank(req.cv_text, req.jobs, req.top_k)
    return RankResponse(
        results=[MatchResult(**r) for r in results],
        model_used="tfidf_vercel",
    )


@app.get("/trends", response_model=TrendResponse)
async def get_trends():
    """
    Prediksi tren skill berdasarkan analisis pasar kerja.
    Saat ini menggunakan data statis — akan diganti LSTM time-series.
    """
    return TrendResponse(
        period="2026-Q2",
        trends=[
            TrendItem(
                skill="python",
                current_demand=0.85,
                predicted_demand=0.90,
                growth_pct=5.88,
            ),
            TrendItem(
                skill="machine learning",
                current_demand=0.72,
                predicted_demand=0.82,
                growth_pct=13.89,
            ),
            TrendItem(
                skill="react",
                current_demand=0.78,
                predicted_demand=0.81,
                growth_pct=3.85,
            ),
            TrendItem(
                skill="docker",
                current_demand=0.65,
                predicted_demand=0.74,
                growth_pct=13.85,
            ),
            TrendItem(
                skill="kubernetes",
                current_demand=0.45,
                predicted_demand=0.58,
                growth_pct=28.89,
            ),
            TrendItem(
                skill="typescript",
                current_demand=0.62,
                predicted_demand=0.70,
                growth_pct=12.90,
            ),
            TrendItem(
                skill="golang",
                current_demand=0.38,
                predicted_demand=0.50,
                growth_pct=31.58,
            ),
            TrendItem(
                skill="aws",
                current_demand=0.70,
                predicted_demand=0.76,
                growth_pct=8.57,
            ),
            TrendItem(
                skill="postgresql",
                current_demand=0.55,
                predicted_demand=0.60,
                growth_pct=9.09,
            ),
            TrendItem(
                skill="fastapi",
                current_demand=0.35,
                predicted_demand=0.48,
                growth_pct=37.14,
            ),
        ],
    )


@app.get("/health")
async def health():
    """Health check — versi Vercel (tanpa TensorFlow model)."""
    return {
        "status": "ok",
        "service": "skillscout-ml-vercel",
        "version": "2.0.0-vercel",
        "model_loaded": False,
        "model_name": None,
        "tokenizer_loaded": False,
        "tokenizer_vocab": 0,
        "max_length": 256,
        "platform": "vercel",
        "matcher": "tfidf_cosine_similarity",
        "note": "TensorFlow tidak tersedia di Vercel (250MB limit). Menggunakan TF-IDF fallback.",
    }


@app.get("/model-info")
async def model_info():
    """Detail arsitektur dan konfigurasi — versi Vercel."""
    return {
        "architecture": "TF-IDF + Cosine Similarity (Vercel)",
        "encoder_name": "skillscout_nusantara",
        "model_name": "tfidf_vercel",
        "config": {
            "max_features": 5000,
            "ngram_range": [1, 2],
            "scoring": "0.6×TF-IDF + 0.4×SkillOverlap",
        },
        "training": {
            "note": "TF-IDF tidak memerlukan training — fit on-the-fly per request",
        },
        "platform": "vercel",
        "model_loaded": False,
        "primary_matcher": "TF-IDF + Cosine Similarity + Skill Overlap",
        "deep_learning_available": False,
        "deep_learning_note": "Gunakan Railway deployment untuk Siamese BiLSTM inference",
        "normalize_skills": list(NORMALIZE.keys()),
    }
