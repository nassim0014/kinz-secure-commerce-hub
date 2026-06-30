# Changelog

All notable changes to **KINZ Secure Commerce Hub** are documented here.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### 🛡️ Security
- **BREAKING:** Removed `python-jose` (CVE-2024-33664 algorithm confusion,
  CVE-2024-33663 JWT-bomb DoS, PYSEC-2025-185 JWE DoS). `PyJWT` is the only
  JWT library now used.
- **BREAKING:** JWT tokens now require `iss`, `aud`, and `jti` claims.
  `verify_token()` validates all three on every request. Tokens issued
  by previous versions will be rejected — re-issue tokens after deploy.
- Fixed critical bug where the demo user's bcrypt hash was an invalid
  placeholder (`Invalid salt` on every login attempt). The hash is now
  read from `DEMO_USER_PASSWORD_HASH` and must be a valid 60-char bcrypt hash.
- `JWT_SECRET` is now validated on startup: must be ≥ 32 chars; the app
  refuses to boot in production if set to a known placeholder.
- Added `enforce_production_safety()` startup check: production refuses
  to start if `DEMO_USER_ENABLED=true`, if CORS includes `*` or `localhost`,
  or if `DATABASE_URL` contains `change_me`.
- Hardened `OWASPHeadersMiddleware`: added `Cross-Origin-Resource-Policy`,
  `Cross-Origin-Opener-Policy`, `Cross-Origin-Embedder-Policy`,
  `X-DNS-Prefetch-Control`, and `base-uri 'none'` to CSP.
- `/docs` and `/redoc` are now disabled when `NODE_ENV=production`.
- Audit logger now rotates (10 MB × 5 files by default) and fails loud
  in production instead of silently falling back to `/tmp`.

### ✨ Added
- `request_id` middleware: every request gets a UUID4 correlation ID
  echoed in `X-Request-ID` and bound to the logging context.
- `.dockerignore` — reduces image size and prevents leaking `.env`,
  `.git`, and `node_modules` into the build context.
- Multi-stage `Dockerfile` (builder + runtime) — no `build-essential`
  in the final image, ~40% smaller.
- `src/frontend/Dockerfile` — production Next.js standalone build.
- `docker-compose.yml` hardened: `read_only: true`, `cap_drop: ALL`,
  `no-new-privileges`, memory/CPU limits, `backend` network is
  `internal: true`, postgres port binds to `127.0.0.1` only.
- `bandit` SAST in CI; `trivy` container scan (HIGH/CRITICAL fail the build);
  SARIF results uploaded to GitHub Security tab.
- Python 3.12 + Node 22 added to CI matrix.
- Coverage reporting via `pytest-cov` + Codecov upload.
- Dependabot config: weekly pip + npm + GitHub Actions + Docker updates.
- `pre-commit` config: ruff, bandit, gitleaks, pytest.
- `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`, `CODEOWNERS`.
- Issue templates: bug report, feature request, security report.
- PR template with security-considerations section.
- `JWT_ISSUER`, `JWT_AUDIENCE`, `AUDIT_LOG_MAX_BYTES`,
  `AUDIT_LOG_BACKUP_COUNT`, `DEMO_USER_*` env vars.
- `LoginRequest.email` is now validated as a real email (`EmailStr`).
- `LoginRequest.password` enforces `min_length=8, max_length=128`.

### 🔧 Changed
- Switched `config.py` from raw `os.getenv` to `pydantic-settings`
  `BaseSettings` — proper type coercion, env-file support, validators.
- `auth.py` no longer hardcodes the demo user's email or password hash;
  both are read from env vars.
- `unhandled_exception_handler` now returns a `request_id` in the
  error body so users can quote it when reporting issues.

### 🗑️ Removed
- `python-jose[cryptography]` (3 CVEs).
- Hardcoded demo credentials from `auth.py` source.

## [1.0.0] — 2025-06-22

Initial public release.

### Added
- FastAPI backend with JWT auth, RBAC, rate limiting, OWASP headers, audit log.
- Next.js 14 dashboard with KPIs, channel breakdown, product performance.
- ETL pipeline (extract → transform → load) with APScheduler.
- PostgreSQL 16 schema (SQLAlchemy ORM).
- Docker + docker-compose one-command stack.
- GitHub Actions CI: ruff, pytest, jest, gitleaks, pip-audit, npm audit.
- SECURITY.md, docs/threat-model.md (STRIDE), docs/deployment.md.
- Real KINZ product catalog (30 SKUs) and 13.7k synthetic sales rows.
- EDA notebook with 3 business insights + Matplotlib/Seaborn charts.
