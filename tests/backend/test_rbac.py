"""Unit tests for the role-based access-control dependencies.

`tests/backend/test_api.py` already covers the happy path and the
missing-header 401 through the live FastAPI dependency wiring. This file
covers the branches that integration test cannot reach directly:

  - `current_user` rejecting a syntactically-invalid / unsigned token
    (the `PyJWTError` handler);
  - `current_user` rejecting a validly-signed token whose `role` claim is
    not one of the three known roles (the "defense in depth" check);
  - the `require_role` dependency factory — its 403 branch and its
    pass-through branch — which no route currently wires up.
"""
import jwt
import pytest
from fastapi import HTTPException, status

from src.api.security.jwt_handler import issue_token
from src.api.security.rbac import current_user, require_role


# ─── current_user: Authorization header parsing ──────────────────────

def test_missing_header_is_401():
    with pytest.raises(HTTPException) as exc:
        current_user(authorization=None)
    assert exc.value.status_code == status.HTTP_401_UNAUTHORIZED
    assert exc.value.headers["WWW-Authenticate"] == "Bearer"


def test_non_bearer_scheme_is_401():
    with pytest.raises(HTTPException) as exc:
        current_user(authorization="Basic dXNlcjpwYXNz")
    assert exc.value.status_code == status.HTTP_401_UNAUTHORIZED


def test_bearer_scheme_is_case_insensitive():
    token = issue_token(subject="u@kinzoils.com", role="viewer")
    claims = current_user(authorization=f"bearer {token}")
    assert claims["sub"] == "u@kinzoils.com"


# ─── current_user: token validation (lines 29-30) ────────────────────

def test_garbage_token_raises_401_not_500():
    """A malformed token must surface as 401, not leak a decode exception."""
    with pytest.raises(HTTPException) as exc:
        current_user(authorization="Bearer not-a-real-jwt")
    assert exc.value.status_code == status.HTTP_401_UNAUTHORIZED
    assert "Invalid token" in exc.value.detail
    assert exc.value.headers["WWW-Authenticate"] == "Bearer"


def test_token_signed_with_wrong_secret_is_401():
    forged = jwt.encode(
        {"sub": "attacker@evil.com", "role": "admin", "iat": 0,
         "exp": 9999999999, "iss": "kinz-secure-commerce-hub",
         "aud": "kinz-api", "jti": "x"},
        "the-wrong-secret-the-attacker-guessed-badly",
        algorithm="HS256",
    )
    with pytest.raises(HTTPException) as exc:
        current_user(authorization=f"Bearer {forged}")
    assert exc.value.status_code == status.HTTP_401_UNAUTHORIZED


# ─── current_user: role-claim allow-list (line 39) ───────────────────

def test_validly_signed_token_with_unknown_role_is_rejected():
    """Signature is good, but `role` is outside {viewer, analyst, admin}.

    This is the "legacy / tampered-by-issuer" guard — a valid signature is
    not enough, the role itself must be recognised.
    """
    token = issue_token(subject="u@kinzoils.com", role="superuser")
    with pytest.raises(HTTPException) as exc:
        current_user(authorization=f"Bearer {token}")
    assert exc.value.status_code == status.HTTP_401_UNAUTHORIZED
    assert "invalid role" in exc.value.detail.lower()


def test_token_with_no_role_claim_is_rejected():
    token = issue_token(subject="u@kinzoils.com", role="viewer", extra={"role": None})
    with pytest.raises(HTTPException) as exc:
        current_user(authorization=f"Bearer {token}")
    assert exc.value.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.parametrize("role", ["viewer", "analyst", "admin"])
def test_each_known_role_is_accepted(role):
    token = issue_token(subject="u@kinzoils.com", role=role)
    claims = current_user(authorization=f"Bearer {token}")
    assert claims["role"] == role


# ─── require_role factory (lines 50-58) ──────────────────────────────

def _claims(role: str) -> dict:
    return {"sub": "u@kinzoils.com", "role": role}


def test_require_role_allows_matching_role():
    checker = require_role("admin")
    claims = _claims("admin")
    assert checker(claims=claims) is claims


def test_require_role_rejects_other_role_with_403():
    """Wrong role is 403 (authenticated but not authorised), never 401."""
    checker = require_role("admin")
    with pytest.raises(HTTPException) as exc:
        checker(claims=_claims("viewer"))
    assert exc.value.status_code == status.HTTP_403_FORBIDDEN
    assert "admin" in exc.value.detail


def test_require_role_accepts_any_of_several_allowed_roles():
    checker = require_role("analyst", "admin")
    assert checker(claims=_claims("analyst")) == _claims("analyst")
    assert checker(claims=_claims("admin")) == _claims("admin")
    with pytest.raises(HTTPException) as exc:
        checker(claims=_claims("viewer"))
    assert exc.value.status_code == status.HTTP_403_FORBIDDEN
    assert "analyst, admin" in exc.value.detail


def test_require_role_missing_role_key_is_403():
    checker = require_role("viewer")
    with pytest.raises(HTTPException) as exc:
        checker(claims={"sub": "u@kinzoils.com"})
    assert exc.value.status_code == status.HTTP_403_FORBIDDEN
