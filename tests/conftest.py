"""Pytest configuration — project root on sys.path so `src.*` imports work."""
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

# Ensure env vars exist for JWT/audit during tests
os.environ.setdefault("JWT_SECRET", "ci-test-secret-32-bytes-or-more-xxxxxx")
os.environ.setdefault("AUDIT_LOG_PATH", "/tmp/kinz-ci-audit.log")

import pytest


@pytest.fixture
def app():
    from src.api.main import app

    return app


@pytest.fixture
def client(app):
    from fastapi.testclient import TestClient

    return TestClient(app)
