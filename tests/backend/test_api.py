"""Integration tests for the FastAPI app via TestClient."""
from src.api.security.jwt_handler import issue_token


def test_health_endpoint(client):
    resp = client.get("/health")
    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] == "ok"
    assert "version" in body


def test_root_endpoint(client):
    resp = client.get("/")
    assert resp.status_code == 200
    body = resp.json()
    assert body["name"] == "KINZ Secure Commerce Hub"


def test_protected_endpoint_requires_token(client):
    resp = client.get("/api/v1/auth/me")
    assert resp.status_code == 401


def test_protected_endpoint_with_valid_token(client):
    token = issue_token(subject="nassim@kinzoils.com", role="admin")
    resp = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["email"] == "nassim@kinzoils.com"
    assert body["role"] == "admin"


def test_products_list_requires_auth(client):
    resp = client.get("/api/v1/products")
    assert resp.status_code == 401


def test_products_list_returns_real_catalog(client):
    token = issue_token(subject="nassim@kinzoils.com", role="admin")
    resp = client.get(
        "/api/v1/products",
        headers={"Authorization": f"Bearer {token}"},
        params={"limit": 5},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["total"] >= 5
    items = body["items"]
    assert len(items) == 5
    # Every product must come from the real KINZ catalog
    for p in items:
        assert p["product_id"].startswith("KINZ-")
        assert p["url"].startswith("https://www.kinzoils.com/products/")
        assert p["price_tnd"] > 0
