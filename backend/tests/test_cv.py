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
async def test_upload_rejects_non_pdf():
    """Upload non-PDF harus ditolak dengan status 400."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/api/cv/upload",
            files={"file": ("test.txt", b"hello world", "text/plain")},
        )
    assert response.status_code == 400
