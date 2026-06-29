# Security Policy

## Supported Versions

KINZ Secure Commerce Hub is under active development. Security fixes are applied to the latest `main` branch.

| Version | Supported          |
|---------|--------------------|
| 1.0.x   | :white_check_mark: |
| < 1.0   | :x:                |

## Reporting a Vulnerability

If you discover a security vulnerability in this repository, please report it responsibly.

- **Email:** security@kinzoils.com
- **PGP:** Available on request
- **Response SLA:** Acknowledgement within 48 hours, assessment within 5 business days.

Please **do not open a public GitHub issue** for security vulnerabilities. Include enough information to reproduce the issue (affected endpoint, payload, expected vs. actual behavior) and avoid exposing sensitive customer data.

## Security Architecture Summary

This project implements a defense-in-depth strategy aligned with the **OWASP Top 10 (2021)** and the **NIST Cybersecurity Framework** (Identify → Protect → Detect → Respond → Recover).

| Layer            | Control                                                                                  |
|------------------|------------------------------------------------------------------------------------------|
| Authentication   | JWT (HS256) with short-lived access tokens; `iss`/`aud`/`jti` claims validated on every request; bcrypt password hashing (12 rounds) |
| Authorization    | Role-based access control (`admin`, `analyst`, `viewer`) enforced per route; role allow-list checked post-decode |
| Transport        | HTTPS enforced in production via Vercel + Render managed certificates; HSTS preload |
| Input Validation | Pydantic v2 schemas on every FastAPI endpoint; `EmailStr` for login; `min_length`/`max_length` on passwords |
| Output Encoding  | React JSX auto-escaping on frontend; structured JSON responses from API |
| Rate Limiting    | Per-IP token bucket (`slowapi`), 120 req/min default; 10 req/min on `/auth/login` |
| Headers          | HSTS, X-Frame-Options: DENY, X-Content-Type-Options: nosniff, CSP, CORP/COEP/COOP, Referrer-Policy, Permissions-Policy |
| Secrets          | `pydantic-settings` BaseSettings with validators; `.env` git-ignored; `gitleaks` in CI; production fails-fast on placeholder secrets |
| Dependencies     | `pip-audit` + `npm audit` + `bandit` SAST + `trivy` container scan on every pull request; SARIF uploaded to GitHub Security tab |
| Audit Logging    | Append-only JSONL audit log of every auth event and sensitive data access; rotates at 10 MB × 5 files; `0600` permissions |
| Container        | Multi-stage build; non-root user (`kinz`, uid 1001); `read_only` rootfs; `cap_drop: ALL`; `no-new-privileges`; memory/CPU limits; `internal: true` backend network |
| Production Safety| App refuses to start if `NODE_ENV=production` and any of: JWT_SECRET is placeholder, DATABASE_URL has weak password, CORS includes `*`/`localhost`, `DEMO_USER_ENABLED=true` |
| Request Tracing  | UUID4 `X-Request-ID` on every request; bound to logging context for SIEM correlation |
| Docs             | `/docs` and `/redoc` disabled when `NODE_ENV=production` to reduce attack surface |

## Threat Model

A STRIDE-based threat model for this architecture is documented in [`docs/threat-model.md`](./docs/threat-model.md).

## Supply-Chain Security

- All dependencies are pinned in `requirements.txt` (backend) and `package.json` with a `package-lock.json` (frontend).
- The CI workflow runs `gitleaks`, `pip-audit`, `npm audit`, `bandit` (SAST), and `trivy` (container image scan) on every pull request.
- Docker images are built from official Python and Node slim base images via multi-stage builds; no compiler toolchain in the runtime image.
- Dependabot submits weekly dependency PRs for pip, npm, GitHub Actions, and Docker base images.
- `pre-commit` hooks (`ruff`, `bandit`, `gitleaks`, `pytest`) run locally before every commit.

## CVE Remediation Log

| Date       | Library         | CVE / ID                  | Action                                                                              |
|------------|-----------------|---------------------------|-------------------------------------------------------------------------------------|
| 2025-06-29 | python-jose     | CVE-2024-33664            | Removed library; migrated to `PyJWT` (the only JWT lib actually used).              |
| 2025-06-29 | python-jose     | CVE-2024-33663 (JWT bomb) | Removed library.                                                                    |
| 2025-06-29 | python-jose     | PYSEC-2025-185 (JWE DoS)  | Removed library.                                                                    |

## Contact

Maintainer: **Nassim K.** — nassim@kinzoils.com
