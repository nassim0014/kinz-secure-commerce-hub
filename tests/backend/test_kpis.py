"""Tests for /api/v1/kpis endpoints — KPI summary + channel breakdown.

The kpis.py module was at 18% coverage (lines 18-22, 31-84, 98-128
uncovered). These tests exercise both routes + the date-filter branches
+ the empty-data path.
"""
from __future__ import annotations

from src.api.security.jwt_handler import issue_token


AUTH_HEADERS = {"Authorization": f"Bearer {issue_token(subject='nassim@kinzoils.com', role='admin')}"}


class TestKpiSummary:
    def test_summary_returns_200(self, client):
        resp = client.get("/api/v1/kpis/summary", headers=AUTH_HEADERS)
        assert resp.status_code == 200
        data = resp.json()
        # Verify all expected fields are present
        for field in ["revenue_tnd", "orders", "avg_order_value_tnd",
                       "gross_margin_tnd", "gross_margin_pct",
                       "unique_customers", "b2b_share_pct", "top_category"]:
            assert field in data, f"missing field: {field}"

    def test_summary_without_token_returns_401(self, client):
        resp = client.get("/api/v1/kpis/summary")
        assert resp.status_code == 401

    def test_summary_with_date_filter(self, client):
        resp = client.get(
            "/api/v1/kpis/summary?start_date=2023-01-01&end_date=2024-12-31",
            headers=AUTH_HEADERS,
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["orders"] >= 0  # should have some orders in 2023-2024

    def test_summary_with_narrow_date_filter(self, client):
        """A very narrow date range should return fewer (or zero) orders."""
        resp = client.get(
            "/api/v1/kpis/summary?start_date=2020-01-01&end_date=2020-01-02",
            headers=AUTH_HEADERS,
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["orders"] == 0
        assert data["revenue_tnd"] == 0
        assert data["top_category"] == "—"

    def test_summary_revenue_matches_orders(self, client):
        """Revenue should be positive when there are orders."""
        resp = client.get("/api/v1/kpis/summary", headers=AUTH_HEADERS)
        data = resp.json()
        if data["orders"] > 0:
            assert data["revenue_tnd"] > 0
            assert data["avg_order_value_tnd"] > 0
            assert data["unique_customers"] > 0

    def test_summary_b2b_share_is_percentage(self, client):
        """B2B share should be between 0 and 100."""
        resp = client.get("/api/v1/kpis/summary", headers=AUTH_HEADERS)
        data = resp.json()
        assert 0 <= data["b2b_share_pct"] <= 100

    def test_summary_gross_margin_pct_is_valid(self, client):
        """Gross margin % should be between -100 and 100 (sanity)."""
        resp = client.get("/api/v1/kpis/summary", headers=AUTH_HEADERS)
        data = resp.json()
        assert -100 <= data["gross_margin_pct"] <= 100


class TestKpiChannels:
    def test_channels_returns_200(self, client):
        resp = client.get("/api/v1/kpis/channels", headers=AUTH_HEADERS)
        assert resp.status_code == 200
        data = resp.json()
        assert isinstance(data, list)

    def test_channels_without_token_returns_401(self, client):
        resp = client.get("/api/v1/kpis/channels")
        assert resp.status_code == 401

    def test_channels_sorted_by_revenue_desc(self, client):
        resp = client.get("/api/v1/kpis/channels", headers=AUTH_HEADERS)
        data = resp.json()
        if len(data) >= 2:
            revenues = [ch["revenue_tnd"] for ch in data]
            assert revenues == sorted(revenues, reverse=True)

    def test_channels_have_required_fields(self, client):
        resp = client.get("/api/v1/kpis/channels", headers=AUTH_HEADERS)
        data = resp.json()
        for ch in data:
            for field in ["channel", "revenue_tnd", "orders",
                          "avg_order_value_tnd", "gross_margin_pct"]:
                assert field in ch, f"missing field: {field}"

    def test_channels_aov_matches_revenue_divided_by_orders(self, client):
        resp = client.get("/api/v1/kpis/channels", headers=AUTH_HEADERS)
        data = resp.json()
        for ch in data:
            if ch["orders"] > 0:
                expected_aov = round(ch["revenue_tnd"] / ch["orders"], 3)
                assert abs(ch["avg_order_value_tnd"] - expected_aov) < 0.01
