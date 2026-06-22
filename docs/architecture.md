# Architecture Notes

High-level architecture diagram lives in `README.md` (Mermaid). This file documents the design decisions.

## Why this split?

- **Next.js** for the dashboard because (a) it's the most recruiter-recognizable React framework, (b) App Router gives us file-based routing and SSR for SEO on public pages, (c) Vercel free tier makes deployment trivial.
- **FastAPI** for the API because (a) async performance is more than enough for our scale, (b) Pydantic v2 gives us strict schema validation for free, (c) OpenAPI/Swagger docs are auto-generated, which auditors love.
- **PostgreSQL** because (a) we need joins and transactions for analytics, (b) it's the same engine Render and most cloud providers offer in managed form.
- **Python ETL** because pandas is the analyst's native tool and keeps the pipeline readable.

## Data flow

1. Raw CSVs land in `data/raw/` (currently a Shopify export — `products.csv`).
2. `src/pipeline/jobs/run_etl.py` loads, validates, and writes processed tables to `data/processed/`.
3. The FastAPI backend reads `data/processed/` (in production this would be Postgres tables populated by the ETL).
4. The Next.js dashboard calls the API and renders charts.

## Why not one big monorepo with a single language?

Because the goal is to demonstrate range. A pure Python stack would say "data engineer"; a pure TypeScript stack would say "frontend dev". The mixed stack says "I can ship a product end-to-end", which is the founder reality at KINZ.
