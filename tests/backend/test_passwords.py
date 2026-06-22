"""Unit tests for password hashing."""
from src.api.security.passwords import hash_password, verify_password


def test_hash_and_verify_password_round_trip():
    plain = "KINZ-demo-2025!"
    hashed = hash_password(plain)
    assert hashed != plain
    assert verify_password(plain, hashed) is True


def test_verify_rejects_wrong_password():
    hashed = hash_password("correct-password")
    assert verify_password("wrong-password", hashed) is False


def test_hash_is_salt_randomized():
    """Two hashes of the same password must differ (salt)."""
    a = hash_password("same-password")
    b = hash_password("same-password")
    assert a != b
    assert verify_password("same-password", a) is True
    assert verify_password("same-password", b) is True
