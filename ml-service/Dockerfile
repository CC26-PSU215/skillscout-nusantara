# ── Build stage ──────────────────────────────────────
FROM python:3.11-slim AS builder

WORKDIR /app

# Install dependencies dulu (cache layer)
COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# ── Runtime stage ────────────────────────────────────
FROM python:3.11-slim

WORKDIR /app

# Copy installed packages
COPY --from=builder /install /usr/local

# Copy app files
COPY . .

# Railway sets PORT env var automatically
ENV PORT=8001
ENV PYTHONUNBUFFERED=1

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:${PORT}/health')" || exit 1

# Start server — use PORT env var (Railway requirement)
CMD uvicorn main:app --host 0.0.0.0 --port ${PORT} --workers 1