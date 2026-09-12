"""Unit tests for role-based access control dependencies.

`src/api/security/rbac.py` sat at 68% coverage with the exception branch
in `current_user()` (invalid/undecodable token), the invalid-role-claim
guard, and the entire `require_role()` factory untested — the highest-value
gap flagged in docs/IMPROVEMENTS.md, since an RBAC bug fails silently
(wrong role let through) rather than loudly.
"""

from fastapi import HTTPException
import pytest

from src.api.security.jwt_handler import issue_token
from src.api.security.rbac import current_user, require_role


def test_current_user_rejects_missing_authorization_header():
    with pytest.raises(HTTPException) as exc_info:
        current_user(authorization=None)
    assert exc_info.value.status_code == 401


def test_current_user_rejects_undecodable_token():
    """Covers the PyJWTError except branch in current_user(): a malformed
    token (not just an expired/tampered one — genuinely undecodable) must
    surface as a 401, not an unhandled exception."""
    with pytest.raises(HTTPException) as exc_info:
        current_user(authorization="Bearer not-a-real-jwt")
    assert exc_info.value.status_code == 401
    assert "Invalid token" in exc_info.value.detail


def test_current_user_rejects_role_outside_allowed_set():
    """Defense-in-depth: a validly-signed token whose role claim isn't one
    of viewer/analyst/admin (e.g. a legacy token minted before role
    validation existed) must still be rejected."""
    token = issue_token(subject="legacy@kinzoils.com", role="viewer", extra={"role": "legacy"})
    with pytest.raises(HTTPException) as exc_info:
        current_user(authorization=f"Bearer {token}")
    assert exc_info.value.status_code == 401
    assert "invalid role" in exc_info.value.detail.lower()


def test_current_user_accepts_each_valid_role():
    for role in ("viewer", "analyst", "admin"):
        token = issue_token(subject="u@kinzoils.com", role=role)
        claims = current_user(authorization=f"Bearer {token}")
        assert claims["role"] == role


def test_require_role_allows_matching_role():
    checker = require_role("admin", "analyst")
    claims = {"sub": "u@kinzoils.com", "role": "admin"}
    assert checker(claims=claims) == claims


def test_require_role_rejects_role_not_in_allowed_set():
    checker = require_role("admin")
    with pytest.raises(HTTPException) as exc_info:
        checker(claims={"sub": "u@kinzoils.com", "role": "viewer"})
    assert exc_info.value.status_code == 403
    assert "admin" in exc_info.value.detail


def test_require_role_with_multiple_allowed_roles():
    checker = require_role("analyst", "admin")
    assert checker(claims={"role": "analyst"})["role"] == "analyst"
    with pytest.raises(HTTPException) as exc_info:
        checker(claims={"role": "viewer"})
    assert exc_info.value.status_code == 403
