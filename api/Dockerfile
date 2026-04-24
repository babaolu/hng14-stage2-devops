# syntax=docker/dockerfile:1
# ── Stage 1: build / dependency resolution ───────────────────────────────────
FROM python:3.12-alpine AS builder

WORKDIR /build

# Alpine needs gcc + musl-dev to compile some Python packages
RUN apk add --no-cache gcc musl-dev libffi-dev

COPY requirements.txt .
RUN pip install --upgrade pip \
    && pip install --no-cache-dir --prefix=/install -r requirements.txt


# ── Stage 2: production image ─────────────────────────────────────────────────
FROM python:3.12-alpine AS runtime

RUN adduser --no-create-home --disabled-password --shell /bin/false appuser

WORKDIR /app

COPY --from=builder /install /usr/local

COPY main.py .

USER appuser

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD wget -qO- http://localhost:8000/health || exit 1

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2"]
