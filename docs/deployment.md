# Cloud Deployment Guide

This guide walks through deploying **KINZ Secure Commerce Hub** to free-tier managed cloud providers. After completing it, you will have:

- A Next.js dashboard running on **Vercel** (free tier).
- A FastAPI backend running on **Render** (free tier).
- A managed PostgreSQL database on **Render** (free tier — 90 days, then upgrade).
- All environment variables wired correctly.
- A live URL you can share with recruiters and stakeholders.

> Total monthly cost at the free tier: **$0**. Production-grade scaling will require upgrading the database and adding Redis for rate-limiting across multiple API instances.

---

## 1. Prerequisites

- A GitHub account with this repository forked or pushed.
- A [Vercel](https://vercel.com) account (sign in with GitHub).
- A [Render](https://render.com) account (sign in with GitHub).
- The `vercel` and `render` CLIs are optional but helpful.

```bash
npm i -g vercel
# Render CLI is installed via: curl -L https://github.com/render-oss/cli/releases/latest/download/render-linux-amd64 -o /usr/local/bin/render && chmod +x /usr/local/bin/render
```

---

## 2. Deploy the Backend (FastAPI) to Render

### 2.1 Create the database

1. Log into Render → **New +** → **PostgreSQL**.
2. Name: `kinz-db`
3. Database: `kinz_commerce`
4. User: `kinz_app`
5. Region: Frankfurt (closest to Tunisia with low latency).
6. Plan: **Free** (or `Starter` for production).
7. Click **Create Database**.
8. Copy the **Internal Database URL** — you'll need it in step 2.2.

### 2.2 Create the API service

1. Render → **New +** → **Web Service**.
2. Connect your GitHub account and select the `kinz-secure-commerce-hub` repo.
3. Configure:
   - **Name:** `kinz-api`
   - **Region:** Frankfurt
   - **Runtime:** Python 3
   - **Root Directory:** `src/api`
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `uvicorn main:app --host 0.0.0.0 --port $PORT`
   - **Plan:** Free
4. Under **Environment**, add the variables from `.env.example`. At minimum:
   ```
   DATABASE_URL=<Internal Database URL from step 2.1>
   JWT_SECRET=<32+ random bytes — use `openssl rand -hex 32`>
   JWT_ALGORITHM=HS256
   JWT_EXPIRE_MINUTES=60
   CORS_ORIGINS=https://kinz-secure-commerce-hub.vercel.app,http://localhost:3000
   AUDIT_LOG_PATH=/tmp/kinz-audit.log
   LOG_LEVEL=INFO
   ```
5. Click **Create Web Service**. Render will build and deploy.
6. Once live, open `https://kinz-api.onrender.com/docs` — you should see the Swagger UI.

### 2.3 Smoke-test the API

```bash
curl https://kinz-api.onrender.com/health
# Expected: {"status":"ok","service":"kinz-secure-commerce-hub","version":"1.0.0"}

curl https://kinz-api.onrender.com/api/v1/products?limit=3
# Expected: 3 KINZ products with real prices in TND
```

---

## 3. Deploy the Frontend (Next.js) to Vercel

### 3.1 Import the project

1. Log into [Vercel](https://vercel.com) → **Add New** → **Project**.
2. Import the `kinz-secure-commerce-hub` repository.
3. Configure:
   - **Framework Preset:** Next.js
   - **Root Directory:** `src/frontend`
   - **Build Command:** `npm run build` (default)
   - **Output Directory:** `.next` (default)
4. Under **Environment Variables**, add:
   ```
   NEXT_PUBLIC_API_URL=https://kinz-api.onrender.com
   NODE_ENV=production
   ```
5. Click **Deploy**. Vercel will build and provide a `*.vercel.app` URL.

### 3.2 (Optional) Custom domain

1. Vercel → Project → **Settings** → **Domains**.
2. Add `kinz.yourdomain.com` → follow DNS instructions.
3. Vercel auto-provisions HTTPS certificates.

---

## 4. Wire the two together

1. Update Render's `CORS_ORIGINS` env var to include your Vercel URL (and custom domain if used).
2. Update Vercel's `NEXT_PUBLIC_API_URL` if your Render URL changes.
3. Redeploy both services to pick up env changes.

---

## 5. Post-Deployment Checklist

- [ ] `https://<vercel-url>/` loads the dashboard without console errors.
- [ ] `https://<render-url>/docs` shows the Swagger UI.
- [ ] `https://<render-url>/health` returns `{"status":"ok"}`.
- [ ] A login attempt with bad credentials returns 401 and is logged to the audit log.
- [ ] `https://www.ssllabs.com/ssltest/` grades both endpoints **A** or **A+**.
- [ ] A new GitHub PR triggers the CI workflow (lint + test + security scan).

---

## 6. Cost & Scaling Notes

| Resource               | Free Tier Limit                            | When to Upgrade                              |
|------------------------|--------------------------------------------|----------------------------------------------|
| Vercel Hobby           | 100 GB bandwidth / month                   | When traffic exceeds ~10k MAU                |
| Render Web Service     | 750 hours / month, sleeps after 15 min idle| When you need always-on API                  |
| Render PostgreSQL      | 90 days free, then $7/mo Starter           | Before the 90-day deadline                   |
| Custom domain + HTTPS  | Free on Vercel                              | —                                            |

When upgrading:
- Move the API to a Render **Starter** instance ($7/mo) for always-on.
- Move Postgres to Render **Starter** ($7/mo) for persistent storage.
- Add a Redis instance (Upstash free tier) for distributed rate limiting.
- Enable Vercel **Pro** for team collaboration and analytics.

---

## 7. Rollback

- **Vercel:** Project → Deployments → promote previous deployment.
- **Render:** Service → Manual Deploy → Deploy from specific commit.
- **Database:** Render Postgres → Backups → restore from snapshot (Starter plan and above only).

---

Last updated: **2025-06-22** — Nassim K.
