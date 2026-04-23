# syntax=docker/dockerfile:1
# ── Stage 1: dependency resolution ───────────────────────────────────────────
FROM python:3.12-slim AS builder

WORKDIR /build

RUN apt-get update \
    && apt-get install -y --no-install-recommends gcc \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --upgrade pip \
    && pip install --no-cache-dir --prefix=/install -r requirements.txt


# ── Stage 2: production image ─────────────────────────────────────────────────
FROM python:3.12-slim AS runtime

RUN useradd --no-create-home --shell /bin/false appuser

WORKDIR /app

COPY --from=builder /install /usr/local

COPY worker.py .

USER appuser

# The worker has no HTTP port, so we healthcheck via a Redis ping script
HEALTHCHECK --interval=30s --timeout=5s --start-period=15s --retries=3 \
    CMD python -c "\
import os, redis; \
r = redis.Redis( \
    host=os.getenv('REDIS_HOST','redis'), \
    port=int(os.getenv('REDIS_PORT',6379)), \
    password=os.getenv('REDIS_PASSWORD'), \
    decode_responses=True \
); \
r.ping()"

CMD ["python", "worker.py"]
