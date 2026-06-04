"""
Router: /api/cv
- POST /api/cv/upload  → upload PDF, ekstrak teks & skills
- GET  /api/cv/{cv_id} → ambil detail CV yang sudah diproses
"""
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends, Header
from typing import Optional
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete

from app.database import get_db
from app.config import settings
from app.db.models import CVUpload
from app.models.schemas import CVUploadResponse
from app.services.cv_parser import extract_text_from_pdf, extract_skills
from app.services.storage import upload_to_supabase, delete_from_supabase

router = APIRouter()

MAX_BYTES = settings.max_cv_size_mb * 1024 * 1024


@router.post("/upload", response_model=CVUploadResponse, status_code=201)
async def upload_cv(
    file: UploadFile = File(...),
    db:   AsyncSession = Depends(get_db),
):
    # 1. Validasi tipe file
    if file.content_type not in settings.allowed_mime_types:
        raise HTTPException(400, detail="Hanya file PDF yang diizinkan.")

    content = await file.read()

    # 2. Validasi ukuran
    if len(content) > MAX_BYTES:
        raise HTTPException(413, detail=f"Ukuran file maksimal {settings.max_cv_size_mb} MB.")

    # 3. Upload ke Supabase Storage
    storage_path = await upload_to_supabase(content, file.filename)

    # 4. Ekstrak teks dari PDF
    raw_text = extract_text_from_pdf(content)

    # 5. Ekstrak daftar skill
    skills = extract_skills(raw_text)

    # 6. Simpan ke database
    cv = CVUpload(
        filename=file.filename,
        storage_path=storage_path,
        raw_text=raw_text,
        skills=skills,
    )
    db.add(cv)
    await db.flush()   # dapatkan id sebelum commit

    return cv


@router.get("/{cv_id}", response_model=CVUploadResponse)
async def get_cv(cv_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(CVUpload).where(CVUpload.id == cv_id))
    cv = result.scalar_one_or_none()
    if not cv:
        raise HTTPException(404, detail="CV tidak ditemukan.")
    return cv


@router.post("/cleanup")
async def cleanup_old_cvs(
    x_api_key: Optional[str] = Header(None, alias="X-API-Key"),
    db: AsyncSession = Depends(get_db),
):
    """
    Endpoint untuk menghapus semua CV yang diupload lebih dari 24 jam yang lalu.
    Menghapus file fisik dari Supabase Storage dan record dari Database.
    Dilindungi dengan API key yang sama dengan endpoint scraping.
    """
    if settings.scrape_api_key and x_api_key != settings.scrape_api_key:
        raise HTTPException(status_code=403, detail="API key tidak valid.")

    cutoff_time = datetime.utcnow() - timedelta(hours=24)
    
    # Ambil CV yang sudah kedaluwarsa
    result = await db.execute(select(CVUpload).where(CVUpload.uploaded_at < cutoff_time))
    expired_cvs = result.scalars().all()

    if not expired_cvs:
        return {"message": "Tidak ada CV kedaluwarsa.", "deleted": 0}

    deleted_count = 0
    for cv in expired_cvs:
        # 1. Hapus dari Supabase Storage
        success = await delete_from_supabase(cv.storage_path)
        if success:
            # 2. Hapus dari Database
            await db.execute(delete(CVUpload).where(CVUpload.id == cv.id))
            deleted_count += 1
            
    # get_db dependency will auto-commit
    return {"message": f"Berhasil menghapus {deleted_count} CV kedaluwarsa.", "deleted": deleted_count}

