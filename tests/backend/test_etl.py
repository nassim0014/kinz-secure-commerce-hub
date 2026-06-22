"""Unit test for the ETL transform layer."""
import pandas as pd

from src.pipeline.jobs.run_etl import transform_products, transform_sales


def test_transform_products_adds_margin_pct():
    df = pd.DataFrame([
        {"product_id": "KINZ-001", "name": "Test Oil", "category": "Vegetable Oils",
         "product_type": "Oil", "price_tnd": 100.0, "cost_tnd": 40.0, "stock_units": 50},
    ])
    out = transform_products(df)
    assert "margin_pct" in out.columns
    assert abs(out.iloc[0]["margin_pct"] - 0.60) < 1e-6


def test_transform_products_drops_invalid_prices():
    df = pd.DataFrame([
        {"product_id": "KINZ-001", "name": "A", "category": "X", "product_type": "",
         "price_tnd": "not-a-number", "cost_tnd": 10.0, "stock_units": 5},
        {"product_id": "KINZ-002", "name": "B", "category": "Y", "product_type": "",
         "price_tnd": 50.0, "cost_tnd": 20.0, "stock_units": 8},
    ])
    out = transform_products(df)
    assert len(out) == 1
    assert out.iloc[0]["product_id"] == "KINZ-002"


def test_transform_sales_adds_year_month_and_quarter():
    df = pd.DataFrame([
        {"order_id": "O1", "order_date": "2024-03-15 10:00", "customer_id": "C1",
         "customer_type": "B2C", "channel": "B2C Web", "product_id": "KINZ-001",
         "quantity": 1, "unit_price_tnd": 30.0, "line_total_tnd": 30.0,
         "order_total_tnd": 30.0, "discount_rate": 0.0},
    ])
    out = transform_sales(df)
    assert out.iloc[0]["year_month"] == "2024-03"
    assert out.iloc[0]["quarter"].startswith("2024Q")
    assert out.iloc[0]["is_b2b"] is False or out.iloc[0]["is_b2b"] == False
