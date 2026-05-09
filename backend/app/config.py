"""
Konfigurasi aplikasi — semua env vars dimuat via pydantic-settings.
Salin `.env.example` → `.env` lalu isi nilainya.
"""
from typing import List

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Memuat semua variabel environment yang diperlukan."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # ── Database ────────────────────────────────────────────
    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/skillscout"

    # ── Supabase Storage ────────────────────────────────────
    supabase_url: str = ""
    supabase_service_key: str = ""
    supabase_bucket: str = "cv-uploads"

    # ── ML Service ──────────────────────────────────────────
    ml_service_url: str = "http://localhost:8001"
    ml_service_timeout: int = 30

    # ── CORS ────────────────────────────────────────────────
    cors_origins: List[str] = ["http://localhost:3000"]

    @field_validator("cors_origins", mode="before")
    @classmethod
    def _parse_cors(cls, v):
        """Terima string JSON dari env var, atau list langsung."""
        if isinstance(v, str):
            import json
            return json.loads(v)
        return v

    # ── JWT (opsional untuk MVP) ────────────────────────────
    jwt_secret: str = "dev-secret-ganti-di-production"
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 60

    # ── Upload ──────────────────────────────────────────────
    max_cv_size_mb: int = 5
    allowed_mime_types: List[str] = [
        "application/pdf",
    ]


# Singleton instance — import `settings` di modul lain
settings = Settings()
