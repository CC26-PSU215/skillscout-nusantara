"""
Vercel Serverless Entry Point
─────────────────────────────
File ini WAJIB ada di api/index.py agar Vercel bisa me-mount
seluruh FastAPI app sebagai satu serverless function.

Vercel akan mencari variabel bernama `app` (atau `handler`)
dari modul ini.
"""
from app.main import app  # noqa: F401 — re-export untuk Vercel

# Vercel secara otomatis mengenali variabel `app` di sini
# sebagai ASGI handler. Tidak perlu kode tambahan.
