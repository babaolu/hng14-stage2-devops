# syntax=docker/dockerfile:1
# ── Stage 1: install production dependencies ──────────────────────────────────
FROM node:20-alpine AS builder

WORKDIR /build

COPY package*.json ./
RUN npm ci --only=production


# ── Stage 2: production image ─────────────────────────────────────────────────
FROM node:20-alpine AS runtime

# Alpine uses adduser, not useradd
RUN adduser --no-create-home --disabled-password --shell /bin/false appuser

WORKDIR /app

COPY --from=builder /build/node_modules ./node_modules
COPY app.js .
COPY views/ ./views/

USER appuser

EXPOSE 3000

# Alpine has wget built in — simpler than spawning a full node process
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD wget -qO- http://localhost:3000/health || exit 1

CMD ["node", "app.js"]
