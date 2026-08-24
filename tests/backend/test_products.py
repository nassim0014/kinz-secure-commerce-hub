"""Tests for /api/v1/products endpoints — catalog list + single lookup.

products.py had no test file at all (72% coverage via incidental hits
from other tests): the entire `/products/{product_id}` single-item
route, the category filter branch, and the empty-catalog fallback in
`_load_products()` were untested.
"""
from __future__ import annotations

from src.api.security.jwt_handler import issue_token

AUTH_HEADERS = {"Authorization": f"Bearer {issue_token(subject='nassim@kinzoils.com', role='admin')}"}


class TestListProducts:
    def test_list_returns_200(self, client):
        resp = client.get("/api/v1/products", headers=AUTH_HEADERS)
        assert resp.status_code == 200
        data = resp.json()
        assert "total" in data
        assert "items" in data
        assert isinstance(data["items"], list)
        assert data["total"] > 0

    def test_list_without_token_returns_401(self, client):
        resp = client.get("/api/v1/products")
        assert resp.status_code == 401

    def test_list_default_limit(self, client):
        resp = client.get("/api/v1/products", headers=AUTH_HEADERS)
        assert resp.status_code == 200
        assert len(resp.json()["items"]) <= 50  # default limit

    def test_list_with_custom_limit(self, client):
        resp = client.get("/api/v1/products?limit=3", headers=AUTH_HEADERS)
        assert resp.status_code == 200
        assert len(resp.json()["items"]) <= 3

    def test_list_with_offset(self, client):
        resp1 = client.get("/api/v1/products?limit=5", headers=AUTH_HEADERS)
        resp2 = client.get("/api/v1/products?limit=5&offset=2", headers=AUTH_HEADERS)
        assert resp1.status_code == 200
        assert resp2.status_code == 200
        if len(resp1.json()["items"]) > 2 and len(resp2.json()["items"]) > 0:
            assert resp1.json()["items"][0]["product_id"] != resp2.json()["items"][0]["product_id"]

    def test_filter_by_category(self, client):
        """Category filter branch (products.py line 32) — not previously exercised."""
        resp = client.get("/api/v1/products?category=Skincare", headers=AUTH_HEADERS)
        assert resp.status_code == 200
        data = resp.json()
        assert data["total"] > 0
        for item in data["items"]:
            assert item["category"].lower() == "skincare"

    def test_filter_by_category_case_insensitive(self, client):
        resp = client.get("/api/v1/products?category=skincare", headers=AUTH_HEADERS)
        assert resp.status_code == 200
        data = resp.json()
        for item in data["items"]:
            assert item["category"].lower() == "skincare"

    def test_filter_by_category_no_match_returns_empty(self, client):
        resp = client.get("/api/v1/products?category=NoSuchCategory", headers=AUTH_HEADERS)
        assert resp.status_code == 200
        data = resp.json()
        assert data["total"] == 0
        assert data["items"] == []

    def test_invalid_limit_below_min(self, client):
        resp = client.get("/api/v1/products?limit=0", headers=AUTH_HEADERS)
        assert resp.status_code == 422

    def test_invalid_limit_above_max(self, client):
        resp = client.get("/api/v1/products?limit=201", headers=AUTH_HEADERS)
        assert resp.status_code == 422

    def test_invalid_offset_negative(self, client):
        resp = client.get("/api/v1/products?offset=-1", headers=AUTH_HEADERS)
        assert resp.status_code == 422

    def test_missing_catalog_file_returns_empty(self, client, monkeypatch, tmp_path):
        """_load_products()'s not-found fallback (products.py line 18)."""
        monkeypatch.setattr("src.api.routes.products.DATA_RAW", tmp_path)
        resp = client.get("/api/v1/products", headers=AUTH_HEADERS)
        assert resp.status_code == 200
        data = resp.json()
        assert data["total"] == 0
        assert data["items"] == []


class TestGetProduct:
    def test_get_existing_product(self, client):
        listing = client.get("/api/v1/products?limit=1", headers=AUTH_HEADERS)
        assert listing.status_code == 200
        items = listing.json()["items"]
        assert items, "fixture catalog should not be empty"
        product_id = items[0]["product_id"]

        resp = client.get(f"/api/v1/products/{product_id}", headers=AUTH_HEADERS)
        assert resp.status_code == 200
        data = resp.json()
        assert data["product_id"] == product_id
        assert "name" in data
        assert "price_tnd" in data

    def test_get_nonexistent_product_returns_404(self, client):
        resp = client.get("/api/v1/products/NONEXISTENT-99999", headers=AUTH_HEADERS)
        assert resp.status_code == 404

    def test_get_product_without_token_returns_401(self, client):
        resp = client.get("/api/v1/products/KINZ-001")
        assert resp.status_code == 401
