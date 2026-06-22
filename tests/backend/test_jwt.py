"""Unit tests for JWT issue / verify helpers."""
import time

import pytest

from src.api.security.jwt_handler import issue_token, verify_token


def test_issue_and_verify_round_trip():
    token = issue_token(subject="nassim@kinzoils.com", role="admin")
    claims = verify_token(token)
    assert claims["sub"] == "nassim@kinzoils.com"
    assert claims["role"] == "admin"
    assert claims["exp"] > claims["iat"]


def test_verify_rejects_tampered_token():
    token = issue_token(subject="user@example.com", role="viewer")
    # Flip the last char of the signature — should fail
    tampered = token[:-1] + ("a" if token[-1] != "a" else "b")
    with pytest.raises(Exception):
        verify_token(tampered)


def test_verify_rejects_expired_token():
    # Issue then artificially expire by monkey-patching settings briefly
    from src.api.utils.config import settings

    token = issue_token(subject="x@y.z", role="viewer")
    # Force expiry check to fail by re-encoding with exp in the past
    import jwt

    expired = jwt.encode(
        {"sub": "x@y.z", "role": "viewer", "iat": 0, "exp": 1},
        settings.JWT_SECRET,
        algorithm=settings.JWT_ALGORITHM,
    )
    with pytest.raises(Exception):
        verify_token(expired)
