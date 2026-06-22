# syntax=docker/dockerfile:1.6
# KINZ Secure Commerce Hub — Backend API image (non-root, slim).

FROM python:3.11-slim AS base

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Create non-root user
RUN groupadd --gid 1001 kinz && \
    useradd  --uid 1001 --gid kinz --create-home --shell /bin/bash kinz

WORKDIR /app

# Install only build deps first (cache layer)
RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential libpq-dev curl \
    && rm -rf /var/lib/apt/lists/*

COPY src/api/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# Copy application code
COPY src/api        /app/src/api
COPY src/pipeline   /app/src/pipeline
COPY data           /app/data

# Ensure audit log dir exists and is writable by kinz
RUN mkdir -p /var/log/kinz && chown -R kinz:kinz /var/log/kinz /app

USER kinz

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
  CMD curl -fs http://localhost:8000/health || exit 1

CMD ["uvicorn", "src.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
