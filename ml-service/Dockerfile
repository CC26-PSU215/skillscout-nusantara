# ═══════════════════════════════════════════════════════════
# SkillScout Nusantara — ML Service Dockerfile
# Platform: Render / Railway / Docker
# ═══════════════════════════════════════════════════════════

FROM python:3.11-slim

WORKDIR /app

# Install dependencies (single layer, no multi-stage untuk Render)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy app files
COPY . .

# Env vars (Render sets PORT automatically)
ENV PORT=8001
ENV PYTHONUNBUFFERED=1
ENV MODEL_PATH=best_model.keras
ENV TOKENIZER_PATH=tokenizer.joblib
ENV MAX_LENGTH=256
ENV BATCH_SIZE=32
ENV ALLOWED_ORIGINS=*

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=120s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:${PORT}/health')" || exit 1

# Start server
CMD uvicorn main:app --host 0.0.0.0 --port ${PORT} --workers 1