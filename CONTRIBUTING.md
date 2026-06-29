# Contributing to KINZ Secure Commerce Hub

First off — thank you for taking the time to contribute. This project is
a solo-maintained portfolio piece, but high-quality PRs from the
community are very welcome.

> **Maintainer:** Nassim K. — nassim@kinzoils.com
> **Response SLA:** Issues reviewed within 5 business days; PRs within 10.

---

## Code of Conduct

By participating in this project you agree to abide by the
[Code of Conduct](./CODE_OF_CONDUCT.md). Please report unacceptable
behavior to nassim@kinzoils.com.

---

## How Can I Contribute?

- **Reporting bugs** — open an issue using the Bug Report template.
- **Suggesting enhancements** — open an issue using the Feature Request template.
- **Reporting security vulnerabilities** — DO NOT open a public issue. See [SECURITY.md](./SECURITY.md).
- **Submitting code** — fork, branch, PR. Read the rest of this file first.

---

## Development Setup

### Prerequisites

- Python 3.11+
- Node.js 20+
- Docker 24+ and Docker Compose v2
- Git 2.30+

### Quick start (Docker — recommended)

```bash
git clone https://github.com/nassim0014/kinz-secure-commerce-hub.git
cd kinz-secure-commerce-hub
cp .env.example .env
# Edit .env: set JWT_SECRET to `python -c "import secrets; print(secrets.token_urlsafe(48))"`
#           set DEMO_USER_PASSWORD_HASH to a real bcrypt hash (see .env.example)
docker compose up --build
```

- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- Swagger docs (dev only): http://localhost:8000/docs

### Local dev (no Docker)

```bash
# Backend
python -m venv .venv && source .venv/bin/activate
pip install -r src/api/requirements.txt
export $(grep -v '^#' .env | xargs)  # load env
cd src/api && uvicorn main:app --reload --port 8000

# Frontend
cd src/frontend
npm install
npm run dev

# Run ETL manually
python -m src.pipeline.jobs.run_etl
```

---

## Git Workflow

1. **Fork & branch.** Branch from `main`:
   - `feat/<short-description>` — new feature
   - `fix/<short-description>` — bug fix
   - `chore/<short-description>` — tooling, deps, refactor
   - `docs/<short-description>` — docs only
   - `security/<short-description>` — security hardening

2. **Write commits.** Use [Conventional Commits](https://www.conventionalcommits.org/):
   ```
   feat(api): add /api/v1/customers endpoint
   fix(auth): reject tokens without iss/aud claims
   chore(deps): bump fastapi to 0.110.1
   docs(readme): add deployment badges
   ```

3. **Keep PRs small.** One logical change per PR. < 400 lines of diff is ideal.

4. **Tests required.** Every PR that touches code must add or update tests
   and keep the full suite green:
   ```bash
   pytest tests/backend/ -q
   cd src/frontend && npm test -- --ci
   ```

5. **Lint must pass.**
   ```bash
   ruff check src/ tests/
   cd src/frontend && npm run lint
   ```

---

## Pre-commit Hooks (recommended)

Install the hooks so linting and secret-scanning happen automatically
on every commit:

```bash
pip install pre-commit
pre-commit install
pre-commit run --all-files  # verify everything passes
```

This will run `ruff`, `bandit`, `gitleaks`, and `pytest` before each
commit. Bypass with `git commit --no-verify` only in emergencies.

---

## Code Style

### Python (backend)
- **Formatter:** `ruff format` (Black-compatible, 88-char line).
- **Linter:** `ruff check` — config in `ruff.toml`.
- **Type hints:** required on all public functions.
- **Imports:** `from __future__ import annotations` is OK except in
  files that use Pydantic models as FastAPI dependencies (the forward-ref
  resolution gets confused — see `auth.py` for the pattern).
- **Tests:** Pytest, `tests/backend/`. Use the `client` fixture from
  `conftest.py` for API integration tests.

### TypeScript (frontend)
- **Formatter:** Prettier (via `next lint --fix`).
- **Linter:** ESLint with `eslint-config-next`.
- **Type strictness:** `strict: true` in `tsconfig.json`.
- **Tests:** Jest, `tests/frontend/`.

---

## Security-sensitive Changes

If your PR touches any of the following, expect extra review time and
please describe the security implications in the PR description:

- `src/api/security/` — auth, JWT, RBAC, audit logging
- `src/api/utils/config.py` — env var handling, secrets
- `Dockerfile` or `docker-compose.yml` — container security
- `.github/workflows/` — CI/CD pipeline
- `SECURITY.md` or `docs/threat-model.md`

---

## Reporting Issues

Use the issue templates in `.github/ISSUE_TEMPLATE/`. If you find a
security issue, follow [SECURITY.md](./SECURITY.md) instead of opening
a public issue.

---

## Release Process

Releases are cut from `main` using [Conventional Commits](https://www.conventionalcommits.org/)
and tagged as `vX.Y.Z`. The changelog is generated automatically.

---

## License

By contributing, you agree that your contributions will be licensed
under the MIT License (see [LICENSE](./LICENSE)).
