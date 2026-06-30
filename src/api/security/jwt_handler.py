"""JWT issue & verify helpers.

Tokens include the standard claims required for robust validation:
  - sub   : subject (user identifier)
  - role  : application role (viewer/analyst/admin)
  - iat   : issued-at (unix ts)
  - exp   : expiry (unix ts)
  - iss   : issuer (validated on decode → defense against token reuse across services)
  - aud   : audience (validated on decode → defense against token reuse across services)
  - jti   : JWT ID (UUID4, enables future revocation / blacklisting)
"""
from __future__ import annotations

import secrets
from datetime import UTC, datetime, timedelta
from typing import Any
from uuid import uuid4

import jwt

from src.api.utils.config import settings


def issue_token(subject: str, role: str = "viewer", extra: dict[str, Any] | None = None) -> str:
    """Issue a signed JWT for `subject` (typically an email or user_id)."""
    now = datetime.now(UTC)
    payload: dict[str, Any] = {
        "sub": subject,
        "role": role,
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(minutes=settings.JWT_EXPIRE_MINUTES)).timestamp()),
        "iss": settings.JWT_ISSUER,
        "aud": settings.JWT_AUDIENCE,
        "jti": str(uuid4()),
    }
    if extra:
        payload.update(extra)
    return jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)


def verify_token(token: str) -> dict[str, Any]:
    """Verify signature, expiry, issuer, and audience.

    Raises jwt.PyJWTError on any failure (signature, expiry, issuer, audience,
    malformed token, missing required claims).
    """
    return jwt.decode(
        token,
        settings.JWT_SECRET,
        algorithms=[settings.JWT_ALGORITHM],
        issuer=settings.JWT_ISSUER,
        audience=settings.JWT_AUDIENCE,
        options={
            "require": ["exp", "iat", "sub", "iss", "aud", "jti"],
            "verify_signature": True,
            "verify_exp": True,
            "verify_iat": True,
            "verify_iss": True,
            "verify_aud": True,
        },
    )


def generate_secret() -> str:
    """Helper for ops: print a fresh 48-byte URL-safe secret for JWT_SECRET."""
    return secrets.token_urlsafe(48)
