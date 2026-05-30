"""
Router: /api/jobs
- GET  /api/jobs       → daftar lowongan (filter & pagination)
- GET  /api/jobs/{id}  → detail satu lowongan
- POST /api/jobs       → tambah lowongan baru (untuk scraper/admin)
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.db.models import Job
from app.models.schemas import JobCreate, JobListResponse, JobResponse

router = APIRouter()


@router.get("", response_model=JobListResponse)
async def list_jobs(
    page: int = Query(1, ge=1, description="Nomor halaman"),
    per_page: int = Query(20, ge=1, le=100, description="Item per halaman"),
    location: str | None = Query(None, description="Filter berdasarkan lokasi"),
    skill: str | None = Query(None, description="Filter berdasarkan skill"),
    search: str | None = Query(None, description="Pencarian judul/perusahaan"),
    db: AsyncSession = Depends(get_db),
):
    """Daftar lowongan dengan pagination dan filter opsional."""
    query = select(Job)

    # Filter opsional
    if location:
        query = query.where(Job.location.ilike(f"%{location}%"))
    if skill:
        # JSONB contains — cari skill di dalam array JSON
        query = query.where(Job.skills.contains([skill]))
    if search:
        query = query.where(
            Job.title.ilike(f"%{search}%") | Job.company.ilike(f"%{search}%")
        )

    # Hitung total
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar_one()

    # Pagination
    query = query.order_by(Job.scraped_at.desc())
    query = query.offset((page - 1) * per_page).limit(per_page)

    result = await db.execute(query)
    jobs = result.scalars().all()

    return JobListResponse(
        total=total,
        page=page,
        per_page=per_page,
        data=jobs,
    )


@router.get("/{job_id}", response_model=JobResponse)
async def get_job(job_id: str, db: AsyncSession = Depends(get_db)):
    """Ambil detail satu lowongan berdasarkan ID."""
    result = await db.execute(select(Job).where(Job.id == job_id))
    job = result.scalar_one_or_none()
    if not job:
        raise HTTPException(404, detail="Lowongan tidak ditemukan.")
    return job


@router.post("", response_model=JobResponse, status_code=201)
async def create_job(payload: JobCreate, db: AsyncSession = Depends(get_db)):
    """Tambah satu lowongan baru (dipanggil scraper atau admin)."""
    job = Job(
        title=payload.title,
        company=payload.company,
        description=payload.description,
        skills=payload.skills,
        location=payload.location,
        source_url=payload.source_url,
    )
    db.add(job)
    await db.flush()
    return job
