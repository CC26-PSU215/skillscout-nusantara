"""
SkillScout Nusantara — FastAPI Application.
"""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.routers import cv, jobs, match, scrape

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifecycle event — start/stop background services.
    Scheduler hanya aktif jika ENABLE_SCRAPE_SCHEDULER=true.
    Di Vercel, gunakan Vercel Cron sebagai gantinya.
    """
    # Startup
    if settings.enable_scrape_scheduler:
        from app.scraping.scheduler import start_scheduler
        start_scheduler()
        logger.info("Background scrape scheduler started")

    yield

    # Shutdown
    if settings.enable_scrape_scheduler:
        from app.scraping.scheduler import stop_scheduler
        stop_scheduler()
        logger.info("Background scrape scheduler stopped")


app = FastAPI(
    title="SkillScout Nusantara API",
    description="Platform Pencari Kerja Berbasis AI untuk Masyarakat Indonesia",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=".*",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(cv.router,     prefix="/api/cv",     tags=["CV"])
app.include_router(jobs.router,   prefix="/api/jobs",   tags=["Jobs"])
app.include_router(match.router,  prefix="/api/match",  tags=["Matching"])
app.include_router(scrape.router, prefix="/api/scrape", tags=["Scraping"])


@app.get("/api/health", tags=["Health"])
async def health():
    return {"status": "ok", "service": "skillscout-api"}

@app.get("/", include_in_schema=False)
async def root():
    return RedirectResponse(url="/api/docs")
