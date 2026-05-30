"""
SkillScout Nusantara — ML Service (Siamese BiLSTM)
Platform: Railway / Render / Docker

Service ini menjalankan model Deep Learning untuk:
  1. POST /rank    → ranking lowongan berdasarkan kecocokan CV (inference)
  2. GET  /trends  → prediksi tren skill (placeholder/time-series)
  3. GET  /health  → health check + info model
  4. GET  /model-info → detail arsitektur & konfigurasi model

Arsitektur Model:
  Siamese BiLSTM — shared encoder (Embedding→BiLSTM×2→Dense→L2Norm)
  Input: tokenized text (cv_input, job_input)
  Output: similarity score 0-1

Environment Variables:
  PORT            — port untuk server (Railway auto-set, default 8001)
  MODEL_PATH      — path ke file .keras (default: best_model.keras)
  TOKENIZER_PATH  — path ke file .joblib (default: tokenizer.joblib)
  MAX_LENGTH      — panjang sequence input (default: 256)
  BATCH_SIZE      — ukuran batch prediksi (default: 32)
  ALLOWED_ORIGINS — comma-separated CORS origins (default: *)
"""

import os
import logging
from pathlib import Path
from contextlib import asynccontextmanager
from typing import Optional

import numpy as np
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

# ── Logging ──────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger("ml-service")

# ── Konfigurasi ──────────────────────────────────────────────
MODEL_PATH = os.getenv("MODEL_PATH", "best_model.keras")
TOKENIZER_PATH = os.getenv("TOKENIZER_PATH", "tokenizer.joblib")
MAX_LENGTH = int(os.getenv("MAX_LENGTH", "256"))
BATCH_SIZE = int(os.getenv("BATCH_SIZE", "32"))

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


# ── Global state ─────────────────────────────────────────────
model = None
tokenizer = None
model_loaded = False


def _load_model():
    """Load model dan tokenizer saat startup. Graceful jika file tidak ada."""
    global model, tokenizer, model_loaded

    # ── Load Keras model ─────────────────────────────────────
    model_file = Path(MODEL_PATH)
    if not model_file.exists():
        logger.warning(
            f"⚠️  Model file '{MODEL_PATH}' tidak ditemukan. "
            "Inference tidak tersedia."
        )
        logger.warning("   Pastikan best_model.keras ada di folder ml-service/")
        return

    try:
        from tensorflow import keras

        # Enable unsafe deserialization untuk Lambda layers
        # (L2Normalize / Dot layer di Siamese model menggunakan lambda)
        keras.config.enable_unsafe_deserialization()

        logger.info(f"📦 Loading model dari '{MODEL_PATH}'...")
        model = keras.models.load_model(str(model_file), safe_mode=False)
        logger.info(f"✅ Model loaded: {model.name}")
    except Exception as e:
        logger.error(f"❌ Gagal load model: {e}")
        return

    # ── Load tokenizer (joblib format — dari ai/model.ipynb) ─
    tokenizer_file = Path(TOKENIZER_PATH)
    if not tokenizer_file.exists():
        logger.warning(
            f"⚠️  Tokenizer file '{TOKENIZER_PATH}' tidak ditemukan."
        )
        logger.warning(
            "   Pastikan tokenizer.joblib ada (export dari ai/model.ipynb)."
        )
        model = None
        return

    try:
        import joblib

        logger.info(f"📦 Loading tokenizer dari '{TOKENIZER_PATH}'...")
        tokenizer = joblib.load(str(tokenizer_file))

        # Verify tokenizer memiliki interface yang dibutuhkan
        vocab_size = len(tokenizer.word_index)
        logger.info(f"✅ Tokenizer loaded (vocab: {vocab_size} words)")
        model_loaded = True

    except Exception as e:
        logger.error(f"❌ Gagal load tokenizer: {e}")
        logger.error("   Detail error untuk debugging:", exc_info=True)
        model = None


# ── Lifespan (startup/shutdown) ──────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    _load_model()
    logger.info(f"🚀 ML Service ready | model_loaded={model_loaded}")
    yield
    logger.info("👋 ML Service shutting down")


# ── FastAPI app ──────────────────────────────────────────────
app = FastAPI(
    title="SkillScout ML Service",
    description=(
        "Siamese BiLSTM inference untuk job-CV matching.\n\n"
        "**Arsitektur:** Shared encoder (Embedding → BiLSTM×2 → Dense → L2Norm) "
        "dengan Dot product similarity.\n\n"
        "**Fallback:** TF-IDF + Cosine Similarity jika model tidak tersedia."
    ),
    version="2.0.0",
    lifespan=lifespan,
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
# Schemas
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
    model_used: str = "siamese_bilstm"


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

def text_to_sequence(text: str) -> np.ndarray:
    """Konversi teks ke padded sequence dengan normalisasi skill."""
    from keras.utils import pad_sequences

    normalized = normalize_skills(text)
    seq = tokenizer.texts_to_sequences([normalized])
    return pad_sequences(
        seq, maxlen=MAX_LENGTH, padding="post", truncating="post"
    )


def batch_predict(cv_text: str, jobs: list[JobPayload]) -> list[float]:
    """
    Batch prediction untuk semua jobs sekaligus (lebih efisien).
    Alih-alih predict satu per satu, kita stack semua input dan predict batch.

    Preprocessing:
      1. Gabungkan description + skills tiap job
      2. Normalize multi-word skills (konsisten dengan training)
      3. Tokenize dan pad ke MAX_LENGTH
      4. Repeat CV sequence untuk setiap job
      5. Batch predict via model
    """
    from keras.utils import pad_sequences

    # Normalize dan tokenize CV
    cv_normalized = normalize_skills(cv_text)
    cv_seq = tokenizer.texts_to_sequences([cv_normalized])
    cv_padded = pad_sequences(
        cv_seq, maxlen=MAX_LENGTH, padding="post", truncating="post"
    )

    # Siapkan semua job sequences (normalize juga)
    job_texts = [
        normalize_skills(f"{j.description} {' '.join(j.skills)}")
        for j in jobs
    ]
    job_seqs = tokenizer.texts_to_sequences(job_texts)
    job_padded = pad_sequences(
        job_seqs, maxlen=MAX_LENGTH, padding="post", truncating="post"
    )

    # Repeat CV sequence untuk setiap job
    cv_repeated = np.repeat(cv_padded, len(jobs), axis=0)

    # Batch predict
    scores = model.predict(
        [cv_repeated, job_padded],
        batch_size=BATCH_SIZE,
        verbose=0,
    ).flatten()

    return scores.tolist()


def compute_skill_match(
    cv_text: str, job_skills: list[str]
) -> tuple[list[str], list[str]]:
    """Hitung matched skills dan gap skills."""
    cv_lower = cv_text.lower()
    job_skill_set = set(s.lower() for s in job_skills)
    matched = sorted(s for s in job_skill_set if s in cv_lower)
    gap = sorted(s for s in job_skill_set if s not in cv_lower)
    return matched, gap


def fallback_tfidf_rank(
    cv_text: str, jobs: list[JobPayload], top_k: int
) -> list[dict]:
    """Fallback TF-IDF + skill overlap jika model tidak tersedia."""
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity

    job_texts = [f"{j.title} {j.description}" for j in jobs]
    corpus = [cv_text] + job_texts

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

    Jika model loaded → gunakan Siamese BiLSTM (batch prediction).
    Jika model TIDAK loaded → fallback ke TF-IDF + cosine similarity.
    """
    if model_loaded and model is not None and tokenizer is not None:
        # ── Deep Learning inference ──
        try:
            scores = batch_predict(req.cv_text, req.jobs)
            results = []
            for idx, job in enumerate(req.jobs):
                matched, gap = compute_skill_match(req.cv_text, job.skills)
                results.append(
                    MatchResult(
                        job_id=job.id,
                        title=job.title,
                        company=job.company,
                        score=round(scores[idx], 4),
                        matched_skills=matched,
                        gap_skills=gap,
                    )
                )
            results.sort(key=lambda x: x.score, reverse=True)
            return RankResponse(
                results=results[: req.top_k],
                model_used="siamese_bilstm",
            )
        except Exception as e:
            logger.error(f"Inference gagal, fallback ke TF-IDF: {e}")

    # ── Fallback TF-IDF ──
    fallback_results = fallback_tfidf_rank(
        req.cv_text, req.jobs, req.top_k
    )
    return RankResponse(
        results=[MatchResult(**r) for r in fallback_results],
        model_used="tfidf_fallback",
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
    """Health check — menampilkan status model."""
    return {
        "status": "ok",
        "service": "skillscout-ml",
        "version": "2.0.0",
        "model_loaded": model_loaded,
        "model_name": model.name if model else None,
        "tokenizer_loaded": tokenizer is not None,
        "tokenizer_vocab": len(tokenizer.word_index) if tokenizer else 0,
        "max_length": MAX_LENGTH,
    }


@app.get("/model-info")
async def model_info():
    """Detail arsitektur dan konfigurasi model."""
    info = {
        "architecture": "Siamese BiLSTM",
        "encoder_name": "skillscout_nusantara",
        "model_name": "siamese_bilstm",
        "config": {
            "vocab_size": 10000,
            "embedding_dim": 300,
            "max_length": MAX_LENGTH,
            "lstm_units_1": 128,
            "lstm_units_2": 64,
            "dense_units": 64,
            "dropout_rate": 0.2,
        },
        "training": {
            "data": "501 CV × 501 Job (Jaccard-based pairs)",
            "loss": "MSE (regression)",
            "optimizer": "Adam (lr=0.001)",
            "epochs_trained": 9,
            "best_val_mae": 0.0169,
            "roc_auc": 0.9997,
        },
        "tokenizer_format": "joblib (Keras Tokenizer)",
        "model_format": ".keras (TensorFlow SavedModel)",
        "model_loaded": model_loaded,
        "fallback": "TF-IDF + Cosine Similarity + Skill Overlap",
        "normalize_skills": list(NORMALIZE.keys()),
    }
    return info


# ── Entry point (untuk development lokal) ────────────────────
if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("PORT", "8001"))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)