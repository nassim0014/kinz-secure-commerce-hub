"""Pytest configuration — project root on sys.path so `src.*` imports work."""
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

# Ensure env vars exist for JWT/audit during tests.
# Use a strong test secret so the validator (>=32 chars) passes.
os.environ.setdefault("JWT_SECRET", "ci-test-secret-32-bytes-or-more-xxxxxx")
os.environ.setdefault("JWT_ISSUER", "kinz-secure-commerce-hub")
os.environ.setdefault("JWT_AUDIENCE", "kinz-api")
os.environ.setdefault("AUDIT_LOG_PATH", "/tmp/kinz-ci-audit.log")  # nosec B108 — CI-only
os.environ.setdefault("DEMO_USER_ENABLED", "true")
os.environ.setdefault("DEMO_USER_EMAIL", "nassim@kinzoils.com")
# Real bcrypt hash for "KINZ-demo-2025!" (12 rounds) — generated with bcrypt.hashpw()
os.environ.setdefault(
    "DEMO_USER_PASSWORD_HASH",
    "$2b$12$90JOIYIldwPChFGagj4hPehUSQIRNFzTHmaaRZm9hyAAmqmo/23iG",
)
os.environ.setdefault("DEMO_USER_ROLE", "admin")
os.environ.setdefault("DEMO_USER_NAME", "Nassim K.")

import pytest  # noqa: E402


@pytest.fixture
def app():
    from src.api.main import app

    return app


@pytest.fixture
def client(app):
    from fastapi.testclient import TestClient

    return TestClient(app)
