# syntax=docker/dockerfile:1.6
# KINZ Secure Commerce Hub — Next.js frontend image (multi-stage, non-root).
#
# Build:
#   docker build -t kinz-web:latest .
# Run:
#   docker run --rm -p 3000:3000 --env-file .env kinz-web:latest

# ────────────────────────────────────────────────────────────
# Stage 1: deps — install node_modules (cached)
# ────────────────────────────────────────────────────────────
FROM node:20-alpine AS deps
WORKDIR /app
COPY package.json package-lock.json* ./
RUN npm ci --no-audit --no-fund 2>/dev/null || npm install --no-audit --no-fund

# ────────────────────────────────────────────────────────────
# Stage 2: builder — compile Next.js
# ────────────────────────────────────────────────────────────
FROM node:20-alpine AS builder
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY . .
ENV NEXT_TELEMETRY_DISABLED=1
RUN npm run build

# ────────────────────────────────────────────────────────────
# Stage 3: runtime — minimal image, non-root, no dev deps
# ────────────────────────────────────────────────────────────
FROM node:20-alpine AS runtime
WORKDIR /app

ENV NODE_ENV=production \
    NEXT_TELEMETRY_DISABLED=1 \
    PORT=3000

# Install curl for healthcheck, then create non-root user
RUN apk add --no-cache curl wget \
    && addgroup --system --gid 1001 nodejs \
    && adduser --system --uid 1001 --ingroup nodejs nextjs

# Copy standalone Next.js output (requires `output: 'standalone'` in next.config.js)
COPY --from=builder --chown=nextjs:nodejs /app/.next/standalone ./
COPY --from=builder --chown=nextjs:nodejs /app/.next/static ./.next/static
COPY --from=builder --chown=nextjs:nodejs /app/public ./public

USER nextjs
EXPOSE 3000

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
  CMD curl -fs http://localhost:3000/ || exit 1

CMD ["node", "server.js"]
