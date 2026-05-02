# Use a lightweight Python image
FROM python:3.12-slim

# Magically copy the blazing-fast 'uv' tool into the container
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

# Copy only the requirements first to cache the installation step
COPY requirements.txt .

# Install dependencies directly into the container system (no venv needed inside Docker)
RUN uv pip install --system -r requirements.txt

# We don't copy the code here because we will mount it in docker-compose for hot-reloading
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]