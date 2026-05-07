"""
Router: /api/cv
- POST /api/cv/upload  → upload PDF, ekstrak teks & skills
- GET  /api/cv/{cv_id} → ambil detail CV yang sudah diproses
"""
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import get_db
from app.config import settings
from app.db.models import CVUpload
from app.models.schemas import CVUploadResponse
from app.services.cv_parser import extract_text_from_pdf, extract_skills
from app.services.storage import upload_to_supabase

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
