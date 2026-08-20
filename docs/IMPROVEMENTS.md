# Improvement backlog

The queue the closed-loop improvement cycle works from. One item per run,
highest value first.

**How to run the workflows locally**

```bash
# Backend tests (37 tests, ~4s)
cd src/api && pip install -r requirements.txt
cd ../.. && pytest tests/ -v

# Backend lint + SAST
cd src/api && ruff check . && bandit -r . -ll -ii -x tests/

# Frontend tests
cd src/frontend && npm install && npx jest

# Full stack via Docker
docker compose up --build -d

# CI: .github/workflows/ci.yml — backend (Python 3.11+3.12) + frontend (Node)
```

---

## Now

### 1. `routes/kpis.py` coverage — 18% → target 100%
78 statements, only 14 covered. The KPI routes are the most complex API
endpoints (aggregation queries, date filtering, margin calculations).
Zero coverage means a silent bug in a KPI calculation would ship without
detection. Same pattern as kinz-competitor-intelligence PRs #43/#44:
`TestClient` against the real FastAPI app, one test per route + filter
branch.

### 2. `routes/sales.py` coverage — 36% → target 100%
33 statements, 21 uncovered. Lower priority than KPIs but same shape.

### 3. ~~`models/db.py` coverage — 0%~~ ✅
13 new tests in `tests/backend/test_models.py`: CRUD on all three ORM
models (ProductORM, CustomerORM, SaleORM) + defaults (stock_units,
marketing_opt_in, autoincrement id) + nullability + metadata inspection
(tables exist, column types). Uses in-memory SQLite so no DB needed.

## Next

### 4. Open dependabot PR #18 — next 14→16 (major runtime bump)
50 days old. Next.js 14→16 is a major runtime bump — per the review-loop
rules, major runtime bumps always wait for the owner. The repo also has a
frontend with its own Dockerfile and tailwind config — the bump needs
manual verification that the frontend still renders correctly.

### 5. No CLAUDE.md
No project-level instructions for AI agents. Adding one would let the
closed-loop work this repo autonomously.

---

## Done

- **PR #1 (this PR)** — Created `docs/IMPROVEMENTS.md` + fixed the
  `SettingWithCopyWarning` in `src/pipeline/jobs/run_etl.py`.

  The warning was real: `transform_products()` did `df = df.dropna(...)`
  (returning a view) then `df["margin_pct"] = ...` (assigning to a view,
  which pandas warns may not propagate to the original). Same issue in
  `transform_sales()`. Fix: added `.copy()` after `dropna` in both
  functions, breaking the view chain.

  37 tests still pass, ruff clean. The warning is gone.

## Dropped

(none yet)
