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
| Authentication   | JWT (HS256) with short-lived access tokens, bcrypt password hashing (12 rounds)          |
| Authorization    | Role-based access control (`admin`, `analyst`, `viewer`) enforced per route              |
| Transport        | HTTPS enforced in production via Vercel + Render managed certificates                    |
| Input Validation | Pydantic v2 schemas on every FastAPI endpoint                                            |
| Output Encoding  | React JSX auto-escaping on frontend; structured JSON responses from API                  |
| Rate Limiting    | Per-IP token bucket (`slowapi`), 120 req/min default                                     |
| Headers          | Strict-Transport-Security, X-Frame-Options: DENY, X-Content-Type-Options: nosniff, CSP   |
| Secrets          | Loaded from environment variables; `.env` is git-ignored; `gitleaks` runs in CI          |
| Dependencies     | `pip-audit` + `npm audit` on every pull request                                          |
| Audit Logging    | Append-only audit log of every auth event and sensitive data access                      |
| Container        | Non-root user in Docker image; read-only filesystem where possible                       |

## Threat Model

A STRIDE-based threat model for this architecture is documented in [`docs/threat-model.md`](./docs/threat-model.md).

## Supply-Chain Security

- All dependencies are pinned in `requirements.txt` (backend) and `package.json` with a `package-lock.json` (frontend).
- The CI workflow runs `gitleaks`, `pip-audit`, and `npm audit` on every pull request.
- Docker images are built from official Python and Node slim base images and rebuilt weekly via a scheduled workflow.

## Contact

Maintainer: **Nassim K.** — nassim@kinzoils.com
