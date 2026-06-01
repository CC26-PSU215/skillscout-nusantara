"""
Background Scheduler — menjalankan scraping otomatis setiap interval.

Menggunakan APScheduler yang jalan di dalam proses FastAPI.
Hanya aktif jika ENABLE_SCRAPE_SCHEDULER=true di env.
Di Vercel (serverless), gunakan Vercel Cron sebagai gantinya.
"""

import logging
from datetime import datetime
from typing import Optional

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger

logger = logging.getLogger(__name__)

# ── Global state ─────────────────────────────────────────────────────────────

_scheduler: Optional[AsyncIOScheduler] = None

# Simpan status scraping terakhir (in-memory)
last_scrape_status: dict = {
    "last_run": None,
    "last_result": None,
    "is_running": False,
    "total_runs": 0,
}


async def run_scrape_job():
    """
    Job function yang dipanggil oleh scheduler atau manual trigger.
    Menjalankan Glints scraper dan menyimpan hasilnya.
    """
    from app.config import settings
    from app.scraping.glints_scraper import GlintsScraper

    if last_scrape_status["is_running"]:
        logger.warning("Scrape job already running, skipping...")
        return last_scrape_status

    last_scrape_status["is_running"] = True
    logger.info("🔍 Starting scheduled scrape job...")

    try:
        scraper = GlintsScraper()
        result = await scraper.scrape_and_save_to_db(
            pages=settings.scrape_pages
        )

        last_scrape_status["last_run"] = datetime.utcnow().isoformat()
        last_scrape_status["last_result"] = result
        last_scrape_status["total_runs"] += 1

        logger.info(
            f"✅ Scrape complete: {result.get('new_inserted', 0)} new jobs"
        )
    except Exception as e:
        logger.error(f"❌ Scrape job failed: {e}")
        last_scrape_status["last_result"] = {"error": str(e)}
    finally:
        last_scrape_status["is_running"] = False

    return last_scrape_status


def start_scheduler():
    """
    Start background scheduler.
    Hanya dipanggil jika ENABLE_SCRAPE_SCHEDULER=true.
    """
    global _scheduler
    from app.config import settings

    if _scheduler is not None:
        logger.warning("Scheduler already running")
        return

    _scheduler = AsyncIOScheduler()
    _scheduler.add_job(
        run_scrape_job,
        trigger=IntervalTrigger(hours=settings.scrape_interval_hours),
        id="glints_scrape",
        name=f"Scrape Glints setiap {settings.scrape_interval_hours} jam",
        replace_existing=True,
    )
    _scheduler.start()
    logger.info(
        f"📅 Scheduler started — scraping setiap "
        f"{settings.scrape_interval_hours} jam"
    )


def stop_scheduler():
    """Stop background scheduler."""
    global _scheduler
    if _scheduler:
        _scheduler.shutdown(wait=False)
        _scheduler = None
        logger.info("Scheduler stopped")
