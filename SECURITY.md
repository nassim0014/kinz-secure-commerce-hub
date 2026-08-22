# Security Policy

## Supported Versions

Only the latest `main` branch is supported with security updates.

## Reporting a Vulnerability

Email: nassim@kinzoils.com

Please include:
- A description of the vulnerability
- Steps to reproduce
- Potential impact
- Suggested fix (if any)

You will receive a response within 48 hours.

## Security Measures

This repo is **security-first** by design:
- JWT authentication with role-based access control (viewer/analyst/admin)
- Rate limiting via `slowapi` on all API routes
- Password hashing with bcrypt (12 rounds)
- Audit logging on every mutation (immutable audit trail)
- CORP/COEP/COOP security headers on all API responses
- `pip-audit` dependency scanning in CI
- `gitleaks` secret detection in CI
- `Trivy` container image scanning
- Demo user mode for development (env-gated, disabled in production)
- Request ID tracking for audit correlation

## GDPR Compliance

- Right-to-erasure: `deleteUserData()` wrapped in `prisma.$transaction`
- Data export: ZIP download with signed URL (7-day expiry)
- Audit trail: every erasure/export recorded as `DataRequest`
