"""Unit tests for JWT issue / verify helpers."""

import base64
import json

import jwt
import pytest

from src.api.security.jwt_handler import issue_token, verify_token


def _b64url_decode(segment: str) -> bytes:
    """Decode a JWT segment, restoring the padding JWT strips."""
    return base64.urlsafe_b64decode(segment + "=" * (-len(segment) % 4))


def test_issue_and_verify_round_trip():
    token = issue_token(subject="nassim@kinzoils.com", role="admin")
    claims = verify_token(token)
    assert claims["sub"] == "nassim@kinzoils.com"
    assert claims["role"] == "admin"
    assert claims["exp"] > claims["iat"]


def test_verify_rejects_tampered_signature():
    """A tampered signature must be rejected.

    This used to flip the LAST character of the signature, which is flaky: a
    32-byte HMAC is 43 base64url characters, and 43*6 = 258 bits encode only
    256, so the final character carries just 2 significant bits. Four of the
    64 possible last characters decode to the same bytes — about 8% of tokens
    ended up "tampered" into a re-spelling of themselves, and verify_token
    correctly did not raise. Measured at 3 failures in 25 identical runs.

    Flipping a character in the middle instead changes a full 6 bits, and the
    assertion below guarantees the bytes really differ, so this test can never
    silently pass by not tampering at all.
    """
    token = issue_token(subject="user@example.com", role="viewer")
    head, payload, signature = token.split(".")

    i = len(signature) // 2
    swapped = "a" if signature[i] != "a" else "b"
    tampered_signature = signature[:i] + swapped + signature[i + 1:]

    # The tamper must actually change the decoded signature, or we are not
    # testing anything.
    assert _b64url_decode(tampered_signature) != _b64url_decode(signature)

    with pytest.raises(jwt.InvalidSignatureError):
        verify_token(f"{head}.{payload}.{tampered_signature}")


def test_verify_rejects_tampered_payload():
    """Editing the claims invalidates the signature — the privilege-escalation case."""
    token = issue_token(subject="user@example.com", role="viewer")
    head, payload, signature = token.split(".")

    claims = json.loads(_b64url_decode(payload))
    assert claims["role"] == "viewer"
    claims["role"] = "admin"
    forged = base64.urlsafe_b64encode(
        json.dumps(claims, separators=(",", ":")).encode()
    ).decode().rstrip("=")

    with pytest.raises(jwt.InvalidSignatureError):
        verify_token(f"{head}.{forged}.{signature}")


def test_verify_rejects_expired_token():
    # Issue then artificially expire by monkey-patching settings briefly
    from src.api.utils.config import settings

    issue_token(subject="x@y.z", role="viewer")
    # Force expiry check to fail by re-encoding with exp in the past
    import jwt

    expired = jwt.encode(
        {"sub": "x@y.z", "role": "viewer", "iat": 0, "exp": 1},
        settings.JWT_SECRET,
        algorithm=settings.JWT_ALGORITHM,
    )
    with pytest.raises(Exception):
        verify_token(expired)
