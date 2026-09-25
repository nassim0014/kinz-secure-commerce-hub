"""Unit test for the ETL transform layer."""
import math

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


def test_transform_products_zero_price_margin_pct_is_not_infinite():
    """A price of 0.0 (e.g. a promo/freebie SKU) is valid numeric data, so
    dropna(subset=["price_tnd", "cost_tnd"]) does not remove the row — but
    (price - cost) / price then divides by zero. That silently produced
    -inf/inf, which is not valid JSON and misrepresents an undefined margin
    as a real number. It must come out as NaN instead, and the row must be
    kept (only the margin is undefined, not the whole product).
    """
    df = pd.DataFrame([
        {"product_id": "KINZ-003", "name": "Free Sample", "category": "X",
         "product_type": "", "price_tnd": 0.0, "cost_tnd": 5.0, "stock_units": 10},
        {"product_id": "KINZ-004", "name": "B", "category": "Y", "product_type": "",
         "price_tnd": 50.0, "cost_tnd": 20.0, "stock_units": 8},
    ])
    out = transform_products(df)
    assert len(out) == 2
    zero_price_row = out[out["product_id"] == "KINZ-003"].iloc[0]
    assert math.isnan(zero_price_row["margin_pct"])
    normal_row = out[out["product_id"] == "KINZ-004"].iloc[0]
    assert abs(normal_row["margin_pct"] - 0.6) < 1e-6


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
    assert not bool(out.iloc[0]["is_b2b"])
