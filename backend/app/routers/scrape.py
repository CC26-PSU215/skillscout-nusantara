"""
Router: /api/scrape
- POST /api/scrape/trigger  → manual trigger scraping
- GET  /api/scrape/status   → lihat status scraping terakhir
"""

from fastapi import APIRouter, HTTPException, Header
from typing import Optional

from app.config import settings
from app.scraping.scheduler import run_scrape_job, last_scrape_status

router = APIRouter()


@router.post("/trigger")
async def trigger_scrape(
    x_api_key: Optional[str] = Header(None, alias="X-API-Key"),
):
    """
    Manual trigger scraping Glints.
    Dilindungi dengan API key (via header X-API-Key).
    Jika SCRAPE_API_KEY tidak di-set di env, endpoint terbuka (dev mode).
    """
    # Cek API key jika dikonfigurasi
    if settings.scrape_api_key and x_api_key != settings.scrape_api_key:
        raise HTTPException(
            status_code=403,
            detail="API key tidak valid. Kirim header X-API-Key.",
        )

    if last_scrape_status["is_running"]:
        raise HTTPException(
            status_code=409,
            detail="Scraping sedang berjalan. Tunggu hingga selesai.",
        )

    # Jalankan scraping
    result = await run_scrape_job()
    return {
        "message": "Scraping selesai",
        "status": result,
    }


@router.get("/status")
async def scrape_status():
    """Lihat status scraping terakhir."""
    return {
        "last_run": last_scrape_status["last_run"],
        "is_running": last_scrape_status["is_running"],
        "total_runs": last_scrape_status["total_runs"],
        "last_result": last_scrape_status["last_result"],
        "config": {
            "interval_hours": settings.scrape_interval_hours,
            "scheduler_enabled": settings.enable_scrape_scheduler,
            "scrape_pages": settings.scrape_pages,
        },
    }
