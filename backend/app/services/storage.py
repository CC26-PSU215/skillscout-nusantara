"""
Service: upload file ke Supabase Storage.
Menyimpan PDF CV pengguna di bucket cloud agar tidak bergantung
pada filesystem Vercel yang ephemeral.
"""
import uuid
from datetime import datetime

from app.config import settings


async def upload_to_supabase(file_bytes: bytes, original_filename: str) -> str:
    """
    Upload file bytes ke Supabase Storage bucket.

    Args:
        file_bytes: konten file dalam bytes
        original_filename: nama asli file dari user

    Returns:
        storage_path: path lengkap file di Supabase Storage
    """
    from supabase import create_client

    supabase = create_client(settings.supabase_url, settings.supabase_service_key)

    # Buat nama unik agar tidak bentrok
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    unique_id = uuid.uuid4().hex[:8]
    extension = original_filename.rsplit(".", 1)[-1] if "." in original_filename else "pdf"
    storage_filename = f"cv/{timestamp}_{unique_id}.{extension}"

    # Upload ke bucket
    supabase.storage.from_(settings.supabase_bucket).upload(
        path=storage_filename,
        file=file_bytes,
        file_options={"content-type": "application/pdf"},
    )

    return storage_filename


async def get_public_url(storage_path: str) -> str:
    """Dapatkan public URL untuk file yang sudah diupload."""
    from supabase import create_client

    supabase = create_client(settings.supabase_url, settings.supabase_service_key)

    response = supabase.storage.from_(settings.supabase_bucket).get_public_url(
        storage_path
    )
    return response
