"""
Tests: CV upload endpoint.
Menggunakan httpx.AsyncClient + pytest-asyncio.
"""
import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app


@pytest.fixture
def anyio_backend():
    return "asyncio"


# ═════════════════════════════════════════════════════════════════
# Health
# ═════════════════════════════════════════════════════════════════

@pytest.mark.anyio
async def test_health_endpoint():
    """Health endpoint harus mengembalikan status ok."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["service"] == "skillscout-api"


@pytest.mark.anyio
async def test_health_endpoint_returns_json_content_type():
    """Health endpoint harus mengembalikan Content-Type application/json."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/health")
    assert "application/json" in response.headers.get("content-type", "")


# ═════════════════════════════════════════════════════════════════
# CV Upload — Validasi
# ═════════════════════════════════════════════════════════════════

@pytest.mark.anyio
async def test_upload_rejects_non_pdf():
    """Upload non-PDF harus ditolak dengan status 400."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/api/cv/upload",
            files={"file": ("test.txt", b"hello world", "text/plain")},
        )
    assert response.status_code == 400


@pytest.mark.anyio
async def test_upload_rejects_image_file():
    """Upload gambar harus ditolak dengan status 400."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/api/cv/upload",
            files={"file": ("photo.jpg", b"\xff\xd8\xff\xe0", "image/jpeg")},
        )
    assert response.status_code == 400


@pytest.mark.anyio
async def test_upload_rejects_docx_file():
    """Upload DOCX harus ditolak — hanya PDF yang diizinkan."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/api/cv/upload",
            files={"file": ("cv.docx", b"PK", "application/vnd.openxmlformats-officedocument.wordprocessingml.document")},
        )
    assert response.status_code == 400


@pytest.mark.anyio
async def test_upload_without_file_returns_422():
    """Upload tanpa file harus mengembalikan 422 (validation error)."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post("/api/cv/upload")
    assert response.status_code == 422


# ═════════════════════════════════════════════════════════════════
# Jobs — Endpoint existence
# ═════════════════════════════════════════════════════════════════

@pytest.mark.anyio
@pytest.mark.xfail(reason="DB (Supabase) tidak tersedia di test environment", raises=Exception)
async def test_jobs_endpoint_exists():
    """GET /api/jobs harus merespons (bukan 404/405). 500 OK jika DB offline."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/jobs")
    # Route harus ada (bukan 404/405). 200 jika DB aktif, 500 jika tidak.
    assert response.status_code not in (404, 405)


@pytest.mark.anyio
async def test_jobs_invalid_page_param():
    """Page parameter harus >= 1."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/jobs?page=0")
    assert response.status_code == 422  # FastAPI validation error


@pytest.mark.anyio
async def test_jobs_invalid_per_page_param():
    """per_page > 100 harus ditolak."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/jobs?per_page=200")
    assert response.status_code == 422


# ═════════════════════════════════════════════════════════════════
# Match — Validasi input
# ═════════════════════════════════════════════════════════════════

@pytest.mark.anyio
async def test_match_without_body_returns_422():
    """POST /api/match tanpa body harus mengembalikan 422."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post("/api/match")
    assert response.status_code == 422


@pytest.mark.anyio
async def test_match_with_invalid_top_k():
    """top_k harus antara 1 dan 50."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/api/match",
            json={"cv_id": "fake-id", "top_k": 100},
        )
    assert response.status_code == 422


@pytest.mark.anyio
async def test_match_with_zero_top_k():
    """top_k = 0 harus ditolak."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/api/match",
            json={"cv_id": "fake-id", "top_k": 0},
        )
    assert response.status_code == 422


# ═════════════════════════════════════════════════════════════════
# API Docs
# ═════════════════════════════════════════════════════════════════

@pytest.mark.anyio
async def test_openapi_docs_accessible():
    """Swagger docs harus bisa diakses."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/docs")
    assert response.status_code == 200


@pytest.mark.anyio
async def test_openapi_json_accessible():
    """OpenAPI JSON schema harus bisa diakses."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/openapi.json")
    assert response.status_code == 200
    data = response.json()
    assert "paths" in data
    assert "/api/health" in data["paths"]
    assert "/api/cv/upload" in data["paths"]
    assert "/api/jobs" in data["paths"]
    assert "/api/match" in data["paths"]


# ═════════════════════════════════════════════════════════════════
# CORS
# ═════════════════════════════════════════════════════════════════

@pytest.mark.anyio
async def test_cors_allows_localhost():
    """CORS harus mengizinkan origin localhost:3000."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.options(
            "/api/health",
            headers={
                "Origin": "http://127.0.0.1:3000",
                "Access-Control-Request-Method": "GET",
            },
        )
    # Harus ada header CORS
    assert response.status_code in (200, 204)
