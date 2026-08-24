# Improvement backlog

The queue the closed-loop improvement cycle works from. One item per run,
highest value first.

**Verify a symptom is still present before trusting this file's headings.**
Items 1 and 2 below sat marked "Now" for four cycles after PRs #27 and #28
had already resolved both (`routes/kpis.py` and `routes/sales.py` were
already at 99%/97% coverage when checked) — the backlog was simply never
ticked off. `pytest --cov` is the source of truth, not this file.

**How to run the workflows locally**

```bash
# Backend tests (95 tests, ~8s)
cd src/api && pip install -r requirements.txt
cd ../.. && pytest tests/ -v --cov=src --cov-report=term-missing

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

### 6. Remaining coverage gaps — pick the highest-value one next
Roughly ranked by real risk, not just missing-line count:

- `src/api/security/rbac.py` — 68% (8/25 missed, lines 29-30, 39, 50-58).
  Role-based access control. Untested branches in an authorization module
  are the highest-value gap left in the codebase — an RBAC bug fails
  silently (wrong role let through) rather than loudly. **Security-review
  territory: read the whole file and understand every branch before
  writing tests, don't just chase the coverage number.**
- `src/pipeline/jobs/scheduler.py` — 0% (24/24 missed). APScheduler
  wrapper; untested but also never exercised by anything except the live
  container, so a test would need to mock APScheduler's `BlockingScheduler`
  rather than actually run jobs on a timer.
- `src/pipeline/jobs/run_etl.py` — 56% (30/68 missed). The bulk of the
  gap is in `transform_products`/`transform_sales`'s edge-case branches
  (missing columns, empty frames) — same file the `SettingWithCopyWarning`
  fix (PR #26 / this backlog's original item 1) already touched once.
- `src/api/main.py` — 85% (11/72 missed, lines 67-73, 146-153, 181-183) —
  likely startup/shutdown lifecycle and error-handler branches, lower
  value than the above since they're exercised indirectly by every other
  test importing `app`.
- `src/api/routes/auth.py`, `security/jwt_handler.py`,
  `security/passwords.py`, `security/audit.py`, `api/utils/__init__.py` —
  smaller gaps (2-11 lines each), mostly exception-handling branches.

## Next

### 4. Open dependabot PR #18 — next 14→16 (major runtime bump)
50+ days old as of the last check. Next.js 14→16 is a major runtime bump —
per the review-loop rules, major runtime bumps always wait for the owner.
The repo also has a frontend with its own Dockerfile and tailwind config —
the bump needs manual verification that the frontend still renders
correctly.

---

## Done

- **PR #36 (this PR)** — Backlog bookkeeping correction (items 1 and 2
  were already resolved in PRs #27/#28 but never ticked off — moved to
  *Done* below with the real history). Same-PR code contribution: added
  `tests/backend/test_products.py` (previously had no test file at all),
  closing `routes/products.py` from 72%→100% coverage — the entire
  single-product `GET /{product_id}` route, the category-filter branch,
  the case-insensitive-filter branch, the no-match-returns-empty branch,
  and `_load_products()`'s missing-file fallback were all untested before
  this PR. 95 tests pass (was 80), ruff and bandit clean. Verified each
  new assertion actually catches a regression by temporarily breaking the
  corresponding code path (disabled the category filter, changed the 404
  to a 200) and confirming the relevant tests failed, then restored.
- **PR #35** — Added a bug-report issue template.
- **PR #34** — Added `SECURITY.md` with a reporting policy.
- **PR #33** — Added `.pre-commit-config.yaml` for ruff.
- **PR #32** — Added `CONTRIBUTING.md` with dev setup + PR workflow.
- **PR #31** — Added a `Makefile` with ruff + check targets.
- **PR #30 (item 5)** — ~~No CLAUDE.md~~ ✅ Added `CLAUDE.md` with ground
  rules, architecture, test commands, known traps (dependabot, the
  `SettingWithCopyWarning` fix, security headers), and loop-engine
  integration.
- **PR #29 (item 3)** — ~~`models/db.py` coverage — 0%~~ ✅ 13 new tests
  in `tests/backend/test_models.py`: CRUD on all three ORM models
  (ProductORM, CustomerORM, SaleORM) + defaults + nullability + metadata
  inspection.
- **PR #28 (item 2)** — ~~`routes/sales.py` coverage — 36% → target
  100%~~ ✅ Covered every filter branch (channel, category, start_date,
  end_date), pagination, the order lookup, and the 404 path. Landed at
  97% (one line remaining, an edge case not worth chasing at the time).
- **PR #27 (item 1)** — ~~`routes/kpis.py` coverage — 18% → target
  100%~~ ✅ Landed at 99%. Neither this PR nor #28 got ticked off here at
  the time — see the note at the top of this file.
- **PR #26** — Created `docs/IMPROVEMENTS.md` as the first-cycle
  deliverable, AND fixed the `SettingWithCopyWarning` in
  `src/pipeline/jobs/run_etl.py`. `transform_products()` did
  `df = df.dropna(...)` (returning a view) then assigned a new column to
  it, which pandas warns may not propagate to the original. Same issue in
  `transform_sales()`. Fixed with `.copy()` after `dropna` in both
  functions.

## Dropped

(none yet)
