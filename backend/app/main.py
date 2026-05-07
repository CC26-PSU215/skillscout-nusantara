from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.routers import cv, jobs, match

app = FastAPI(
    title="SkillScout Nusantara API",
    description="Platform Pencari Kerja Berbasis AI untuk Masyarakat Indonesia",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(cv.router,    prefix="/api/cv",   tags=["CV"])
app.include_router(jobs.router,  prefix="/api/jobs", tags=["Jobs"])
app.include_router(match.router, prefix="/api/match",tags=["Matching"])


@app.get("/api/health", tags=["Health"])
async def health():
    return {"status": "ok", "service": "skillscout-api"}
