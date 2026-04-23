# syntax=docker/dockerfile:1
# ── Stage 1: install production dependencies ──────────────────────────────────
FROM node:20-slim AS builder

WORKDIR /build

# Copy lockfile + manifest first for layer caching
COPY package*.json ./
RUN npm ci --only=production


# ── Stage 2: production image ─────────────────────────────────────────────────
FROM node:20-slim AS runtime

RUN useradd --no-create-home --shell /bin/false appuser

WORKDIR /app

# Only copy what's needed — no devDependencies, no build tools
COPY --from=builder /build/node_modules ./node_modules
COPY app.js .
COPY views/ ./views/

USER appuser

EXPOSE 3000

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD node -e "require('http').get('http://localhost:3000/health', r => process.exit(r.statusCode === 200 ? 0 : 1)).on('error', () => process.exit(1))"

CMD ["node", "app.js"]
