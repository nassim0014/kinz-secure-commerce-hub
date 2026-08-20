"""Tests for /api/v1/sales endpoints — list + filter + order lookup.

sales.py was at 36% coverage (only the happy path of list_sales was
exercised by test_api.py's smoke test). These tests cover every filter
branch (channel, category, start_date, end_date), pagination (limit +
offset), the order lookup, and the 404 path.
"""
from __future__ import annotations

from src.api.security.jwt_handler import issue_token

AUTH_HEADERS = {"Authorization": f"Bearer {issue_token(subject='nassim@kinzoils.com', role='admin')}"}


class TestListSales:
    def test_list_returns_200(self, client):
        resp = client.get("/api/v1/sales", headers=AUTH_HEADERS)
        assert resp.status_code == 200
        data = resp.json()
        assert "total" in data
        assert "items" in data
        assert isinstance(data["items"], list)
        assert data["total"] >= 0

    def test_list_without_token_returns_401(self, client):
        resp = client.get("/api/v1/sales")
        assert resp.status_code == 401

    def test_list_default_limit(self, client):
        resp = client.get("/api/v1/sales", headers=AUTH_HEADERS)
        assert resp.status_code == 200
        data = resp.json()
        assert len(data["items"]) <= 100  # default limit

    def test_list_with_custom_limit(self, client):
        resp = client.get("/api/v1/sales?limit=5", headers=AUTH_HEADERS)
        assert resp.status_code == 200
        data = resp.json()
        assert len(data["items"]) <= 5

    def test_list_with_offset(self, client):
        """Offset skips the first N rows."""
        resp1 = client.get("/api/v1/sales?limit=10", headers=AUTH_HEADERS)
        resp2 = client.get("/api/v1/sales?limit=10&offset=5", headers=AUTH_HEADERS)
        assert resp1.status_code == 200
        assert resp2.status_code == 200
        # If there are >5 rows, the second response's first item should
        # differ from the first response's first item
        if len(resp1.json()["items"]) > 5 and len(resp2.json()["items"]) > 0:
            assert resp1.json()["items"][0]["order_id"] != resp2.json()["items"][0]["order_id"]

    def test_filter_by_channel(self, client):
        """Filter by channel=B2C Web."""
        resp = client.get("/api/v1/sales?channel=B2C Web", headers=AUTH_HEADERS)
        assert resp.status_code == 200
        data = resp.json()
        for item in data["items"]:
            assert item["channel"].lower() == "b2c web"

    def test_filter_by_channel_case_insensitive(self, client):
        """Channel filter is case-insensitive."""
        resp = client.get("/api/v1/sales?channel=b2c web", headers=AUTH_HEADERS)
        assert resp.status_code == 200
        data = resp.json()
        for item in data["items"]:
            assert item["channel"].lower() == "b2c web"

    def test_filter_by_category(self, client):
        """Filter by category=Body Care."""
        resp = client.get("/api/v1/sales?category=Body Care", headers=AUTH_HEADERS)
        assert resp.status_code == 200
        data = resp.json()
        for item in data["items"]:
            assert item["category"].lower() == "body care"

    def test_filter_by_category_case_insensitive(self, client):
        """Category filter is case-insensitive."""
        resp = client.get("/api/v1/sales?category=body care", headers=AUTH_HEADERS)
        assert resp.status_code == 200
        data = resp.json()
        for item in data["items"]:
            assert item["category"].lower() == "body care"

    def test_filter_by_start_date(self, client):
        """Only orders on or after start_date."""
        resp = client.get(
            "/api/v1/sales?start_date=2024-01-01",
            headers=AUTH_HEADERS,
        )
        assert resp.status_code == 200
        data = resp.json()
        for item in data["items"]:
            assert item["order_date"][:10] >= "2024-01-01"

    def test_filter_by_end_date(self, client):
        """Only orders on or before end_date."""
        resp = client.get(
            "/api/v1/sales?end_date=2023-12-31",
            headers=AUTH_HEADERS,
        )
        assert resp.status_code == 200
        data = resp.json()
        for item in data["items"]:
            assert item["order_date"][:10] <= "2023-12-31"

    def test_filter_combination(self, client):
        """Multiple filters narrow the result set."""
        resp = client.get(
            "/api/v1/sales?channel=B2C Web&category=Body Care&start_date=2023-01-01&end_date=2024-12-31",
            headers=AUTH_HEADERS,
        )
        assert resp.status_code == 200
        data = resp.json()
        for item in data["items"]:
            assert item["channel"].lower() == "b2c web"
            assert item["category"].lower() == "body care"

    def test_invalid_limit_below_min(self, client):
        """limit=0 should fail validation (ge=1)."""
        resp = client.get("/api/v1/sales?limit=0", headers=AUTH_HEADERS)
        assert resp.status_code == 422

    def test_invalid_limit_above_max(self, client):
        """limit=1001 should fail validation (le=1000)."""
        resp = client.get("/api/v1/sales?limit=1001", headers=AUTH_HEADERS)
        assert resp.status_code == 422

    def test_invalid_offset_negative(self, client):
        """offset=-1 should fail validation (ge=0)."""
        resp = client.get("/api/v1/sales?offset=-1", headers=AUTH_HEADERS)
        assert resp.status_code == 422


class TestGetOrder:
    def test_get_existing_order(self, client):
        """Look up an order by its order_id."""
        # First list to get a known order_id
        resp = client.get("/api/v1/sales?limit=1", headers=AUTH_HEADERS)
        assert resp.status_code == 200
        items = resp.json()["items"]
        if items:
            order_id = items[0]["order_id"]
            resp2 = client.get(f"/api/v1/sales/order/{order_id}", headers=AUTH_HEADERS)
            assert resp2.status_code == 200
            data = resp2.json()
            assert data["order_id"] == order_id
            assert isinstance(data["items"], list)
            assert len(data["items"]) >= 1

    def test_get_nonexistent_order_returns_404(self, client):
        """A non-existent order_id returns 404."""
        resp = client.get("/api/v1/sales/order/NONEXISTENT-99999", headers=AUTH_HEADERS)
        assert resp.status_code == 404

    def test_get_order_without_token_returns_401(self, client):
        resp = client.get("/api/v1/sales/order/ORD-01000")
        assert resp.status_code == 401
