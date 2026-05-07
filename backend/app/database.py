"""
Async SQLAlchemy engine + session factory + dependency injection.
Menggunakan asyncpg sebagai driver PostgreSQL.
"""
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase

from app.config import settings

# ── Engine ──────────────────────────────────────────────────
engine = create_async_engine(
    settings.database_url,
    echo=False,          # set True untuk debug query SQL
    pool_pre_ping=True,  # deteksi koneksi mati
    pool_size=5,
    max_overflow=10,
)

# ── Session factory ─────────────────────────────────────────
async_session = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


# ── Base class untuk ORM models ─────────────────────────────
class Base(DeclarativeBase):
    """Base declarative class — semua model inherit dari sini."""
    pass


# ── Dependency: session per-request ─────────────────────────
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Yield satu AsyncSession per request.
    Otomatis commit saat sukses, rollback saat exception.
    """
    async with async_session() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
