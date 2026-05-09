"""
Router: /api/match
- POST /api/match          → cocokkan CV dengan semua lowongan, kembalikan top-K
- GET  /api/match/trends   → prediksi tren skill (dari ML service)
"""
import httpx
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.config import settings
from app.database import get_db
from app.db.models import CVUpload, Job, MatchLog
from app.models.schemas import MatchRequest, MatchResponse, TrendResponse
from app.services.matcher import rank_jobs

router = APIRouter()


@router.post("", response_model=MatchResponse)
async def match_cv_to_jobs(
    payload: MatchRequest,
    db:      AsyncSession = Depends(get_db),
):
    # 1. Ambil CV
    cv_result = await db.execute(select(CVUpload).where(CVUpload.id == payload.cv_id))
    cv = cv_result.scalar_one_or_none()
    if not cv:
        raise HTTPException(404, detail="CV tidak ditemukan.")

    # 2. Ambil semua job dari DB
    job_result = await db.execute(select(Job))
    jobs = job_result.scalars().all()

    if not jobs:
        raise HTTPException(404, detail="Belum ada data lowongan.")

    # 3. Panggil ML service (Railway/Render) — atau gunakan local matcher
    try:
        results = await _call_ml_service(cv.raw_text, jobs, payload.top_k)
    except httpx.RequestError:
        # Fallback ke local TF-IDF jika ML service tidak tersedia
        results = rank_jobs(cv.raw_text, cv.skills, jobs, payload.top_k)

    # 4. Log hasil ke database
    for item in results:
        log = MatchLog(
            cv_id=cv.id,
            job_id=item["job"].id,
            score=item["score"],
            matched_skills=item["matched_skills"],
            gap_skills=item["gap_skills"],
        )
        db.add(log)

    return MatchResponse(cv_id=payload.cv_id, results=results)


@router.get("/trends", response_model=TrendResponse)
async def get_skill_trends():
    """Meneruskan request ke ML service untuk prediksi tren skill."""
    async with httpx.AsyncClient(timeout=settings.ml_service_timeout) as client:
        try:
            resp = await client.get(f"{settings.ml_service_url}/trends")
            resp.raise_for_status()
            return resp.json()
        except httpx.RequestError:
            raise HTTPException(503, detail="ML service sedang tidak tersedia.")


async def _call_ml_service(cv_text: str, jobs: list, top_k: int) -> list:
    """Kirim teks CV dan daftar job ke ML service, terima ranking hasil."""
    payload = {
        "cv_text": cv_text,
        "jobs": [{"id": j.id, "description": j.description, "skills": j.skills} for j in jobs],
        "top_k": top_k,
    }
    async with httpx.AsyncClient(timeout=settings.ml_service_timeout) as client:
        resp = await client.post(f"{settings.ml_service_url}/rank", json=payload)
        resp.raise_for_status()
        return resp.json()["results"]
