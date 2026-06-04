"""
Async SQLAlchemy engine + session factory + dependency injection.
Menggunakan asyncpg sebagai driver PostgreSQL.
Kompatibel dengan Supabase PgBouncer (transaction pooling mode).

FIX: DuplicatePreparedStatementError
  Supabase menggunakan PgBouncer dalam transaction pooling mode.
  Pada mode ini, koneksi di-share antar client setelah setiap transaksi.
  asyncpg secara default menggunakan prepared statements yang di-cache,
  tapi PgBouncer tidak mendukung ini — menyebabkan error:
    "prepared statement __asyncpg_stmt_2__ already exists"

  Solusi:
    1. statement_cache_size=0     → matikan cache prepared statement
    2. prepared_statement_cache_size=0 → matikan juga di asyncpg
    3. NullPool                   → tiap request buat koneksi baru
       (wajib untuk Vercel serverless, aman juga untuk Railway/Render)
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

# ── Detect PgBouncer ────────────────────────────────────────
# Supabase PgBouncer biasanya di port 6543.
# Jika menggunakan PgBouncer, kita HARUS pakai NullPool
# dan matikan prepared statement caching.
_db_url = str(settings.database_url)
_is_pgbouncer = ":6543/" in _db_url or os.environ.get("PGBOUNCER", "") == "1"
_is_serverless = os.environ.get("VERCEL", "") == "1"

# ── Engine ──────────────────────────────────────────────────
# Gunakan NullPool jika:
#   - Deployment serverless (Vercel) → tiap invocation buat koneksi baru
#   - PgBouncer aktif → hindari cache collision antar shared connections
#
# connect_args:
#   - statement_cache_size=0: Matikan caching prepared statements di asyncpg.
#     Ini WAJIB saat menggunakan PgBouncer transaction pooling mode.
#     Tanpa ini, asyncpg akan error "prepared statement already exists"
#     karena PgBouncer men-share koneksi PostgreSQL antar client.
#   - prepared_statement_cache_size=0: Double-protection untuk asyncpg.
_use_null_pool = _is_serverless or _is_pgbouncer

engine = create_async_engine(
    settings.database_url,
    echo=False,
    pool_pre_ping=True,
    connect_args={
        # ── FIX DuplicatePreparedStatementError ──────────────
        # Kedua parameter ini WAJIB saat pakai PgBouncer.
        "statement_cache_size": 0,
        "prepared_statement_cache_size": 0,
    },
    # NullPool = tidak ada connection pool.
    # Setiap session membuat koneksi baru dan langsung menutupnya.
    # Ini menghindari prepared statement collision di PgBouncer.
    **( {"poolclass": NullPool} if _use_null_pool else {
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
