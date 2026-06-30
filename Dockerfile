# syntax=docker/dockerfile:1.6
# KINZ Secure Commerce Hub — Backend API image (multi-stage, non-root, slim).
#
# Build:
#   docker build -t kinz-secure-commerce-hub:latest .
# Run:
#   docker run --rm -p 8000:8000 --env-file .env kinz-secure-commerce-hub:latest

# ────────────────────────────────────────────────────────────
# Stage 1: builder — install deps into a venv
# ────────────────────────────────────────────────────────────
FROM python:3.11-slim AS builder

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Build deps only
RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Create venv and install deps
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:${PATH}"

WORKDIR /build
COPY src/api/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# ────────────────────────────────────────────────────────────
# Stage 2: runtime — minimal image, no compiler toolchain
# ────────────────────────────────────────────────────────────
FROM python:3.11-slim AS runtime

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH="/opt/venv/bin:${PATH}" \
    PYTHONDONTWRITEBYTECODE=1

# Runtime deps only (no build-essential)
RUN apt-get update && apt-get install -y --no-install-recommends \
        libpq5 curl \
    && rm -rf /var/lib/apt/lists/* \
    && groupadd --gid 1001 kinz \
    && useradd  --uid 1001 --gid kinz --create-home --shell /bin/bash kinz

# Copy the venv from the builder
COPY --from=builder /opt/venv /opt/venv

WORKDIR /app

# Copy application code (data/ is mounted as a volume in compose,
# but we copy a read-only fallback for standalone runs)
COPY --chown=kinz:kinz src/api      /app/src/api
COPY --chown=kinz:kinz src/pipeline /app/src/pipeline
COPY --chown=kinz:kinz data         /app/data

# Ensure audit log dir exists and is writable by kinz
RUN mkdir -p /var/log/kinz && chown -R kinz:kinz /var/log/kinz /app

USER kinz

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
  CMD curl -fs http://localhost:8000/health || exit 1

CMD ["uvicorn", "src.api.main:app", "--host", "0.0.0.0", "--port", "8000", "--no-access-log"]
