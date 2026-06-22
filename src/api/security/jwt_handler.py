"""JWT issue & verify helpers."""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any

import jwt

from src.api.utils.config import settings


def issue_token(subject: str, role: str = "viewer", extra: dict[str, Any] | None = None) -> str:
    """Issue a signed JWT for `subject` (typically an email or user_id)."""
    now = datetime.now(timezone.utc)
    payload: dict[str, Any] = {
        "sub": subject,
        "role": role,
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(minutes=settings.JWT_EXPIRE_MINUTES)).timestamp()),
    }
    if extra:
        payload.update(extra)
    return jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)


def verify_token(token: str) -> dict[str, Any]:
    """Verify signature and expiry. Raises jwt.PyJWTError on failure."""
    return jwt.decode(
        token,
        settings.JWT_SECRET,
        algorithms=[settings.JWT_ALGORITHM],
        options={"require": ["exp", "iat", "sub"]},
    )
