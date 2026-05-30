"""
Async SQLAlchemy engine + session factory + dependency injection.
Menggunakan asyncpg sebagai driver PostgreSQL.
Kompatibel dengan Vercel serverless (NullPool).
"""
import os
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.pool import NullPool

from app.config import settings

# ── Engine ──────────────────────────────────────────────────
# Gunakan NullPool untuk serverless (Vercel) agar tiap invocation
# membuat koneksi baru dan langsung menutupnya.
_is_serverless = os.environ.get("VERCEL", "") == "1"

engine = create_async_engine(
    settings.database_url,
    echo=False,
    pool_pre_ping=True,
    **( {"poolclass": NullPool} if _is_serverless else {
        "pool_size": 5,
        "max_overflow": 10,
    }),
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
