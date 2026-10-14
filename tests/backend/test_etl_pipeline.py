"""Coverage for run_etl.py's extract/load/run functions and scheduler.py.

Before this file, extract_products(), extract_sales(), load() and run()
in run_etl.py had zero test coverage (57% on the module - the only
tested functions were transform_products/transform_sales), and
scheduler.py was never imported by anything in the test suite at all
(0% coverage). These are the functions that actually touch the
filesystem and wire the nightly cron job - the ones most likely to
break silently in production.
"""
from __future__ import annotations

import shutil
from pathlib import Path

import pandas as pd
import pytest

from src.pipeline.jobs import run_etl

REAL_PRODUCTS_CSV = Path(__file__).resolve().parents[2] / "data" / "raw" / "products.csv"
REAL_SALES_CSV = Path(__file__).resolve().parents[2] / "data" / "processed" / "sales_2023_2024.csv"


# ---------------------------------------------------------------------------
# extract_products / extract_sales
# ---------------------------------------------------------------------------


def test_extract_products_reads_real_csv(monkeypatch, tmp_path):
    raw_dir = tmp_path / "raw"
    raw_dir.mkdir()
    shutil.copy(REAL_PRODUCTS_CSV, raw_dir / "products.csv")
    monkeypatch.setattr(run_etl, "DATA_RAW", raw_dir)

    df = run_etl.extract_products()
    expected = pd.read_csv(REAL_PRODUCTS_CSV)
    assert len(df) == len(expected)
    assert "product_id" in df.columns


def test_extract_products_missing_file_raises(monkeypatch, tmp_path):
    monkeypatch.setattr(run_etl, "DATA_RAW", tmp_path)
    with pytest.raises(FileNotFoundError, match="products.csv"):
        run_etl.extract_products()


def test_extract_sales_reads_real_csv(monkeypatch, tmp_path):
    processed_dir = tmp_path / "processed"
    processed_dir.mkdir()
    shutil.copy(REAL_SALES_CSV, processed_dir / "sales_2023_2024.csv")
    monkeypatch.setattr(run_etl, "DATA_PROCESSED", processed_dir)

    df = run_etl.extract_sales()
    expected = pd.read_csv(REAL_SALES_CSV)
    assert len(df) == len(expected)
    assert "order_id" in df.columns


def test_extract_sales_missing_file_raises(monkeypatch, tmp_path):
    monkeypatch.setattr(run_etl, "DATA_PROCESSED", tmp_path)
    with pytest.raises(FileNotFoundError, match="sales_2023_2024.csv"):
        run_etl.extract_sales()


# ---------------------------------------------------------------------------
# transform_* branches not covered by the existing tests
# ---------------------------------------------------------------------------


def test_transform_products_missing_required_column_raises():
    df = pd.DataFrame([{"product_id": "KINZ-001", "name": "X", "category": "Y"}])  # no price/cost
    with pytest.raises(ValueError, match="missing columns"):
        run_etl.transform_products(df)


def test_transform_sales_drops_invalid_rows_and_warns(caplog):
    df = pd.DataFrame(
        [
            {"order_id": "O1", "order_date": "not-a-date", "customer_id": "C1",
             "customer_type": "B2C", "quantity": 1, "unit_price_tnd": 10.0,
             "line_total_tnd": 10.0, "order_total_tnd": 10.0},
            {"order_id": "O2", "order_date": "2024-01-01", "customer_id": "C2",
             "customer_type": "B2B", "quantity": 2, "unit_price_tnd": 5.0,
             "line_total_tnd": 10.0, "order_total_tnd": 10.0},
        ]
    )
    out = run_etl.transform_sales(df)
    assert len(out) == 1
    assert out.iloc[0]["order_id"] == "O2"
    assert bool(out.iloc[0]["is_b2b"]) is True


# ---------------------------------------------------------------------------
# load()
# ---------------------------------------------------------------------------


def test_load_writes_csvs_and_returns_stats(monkeypatch, tmp_path):
    processed_dir = tmp_path / "processed"
    monkeypatch.setattr(run_etl, "DATA_PROCESSED", processed_dir)

    df_products = pd.DataFrame([{"product_id": "KINZ-001", "margin_pct": 0.5}])
    df_sales = pd.DataFrame([{"order_id": "O1"}, {"order_id": "O2"}])

    stats = run_etl.load(df_products, df_sales)

    products_out = processed_dir / "products_enriched.csv"
    sales_out = processed_dir / "sales_enriched.csv"
    assert products_out.exists()
    assert sales_out.exists()
    assert pd.read_csv(products_out).shape[0] == 1
    assert pd.read_csv(sales_out).shape[0] == 2

    assert stats["products_rows"] == 1
    assert stats["sales_rows"] == 2
    assert stats["products_path"] == str(products_out)
    assert stats["sales_path"] == str(sales_out)
    assert "ran_at" in stats


# ---------------------------------------------------------------------------
# run() - full pipeline, end to end, against real seed data
# ---------------------------------------------------------------------------


def test_run_end_to_end_against_real_seed_data(monkeypatch, tmp_path):
    raw_dir = tmp_path / "raw"
    processed_dir = tmp_path / "processed"
    raw_dir.mkdir()
    processed_dir.mkdir()
    shutil.copy(REAL_PRODUCTS_CSV, raw_dir / "products.csv")
    shutil.copy(REAL_SALES_CSV, processed_dir / "sales_2023_2024.csv")

    monkeypatch.setattr(run_etl, "DATA_RAW", raw_dir)
    monkeypatch.setattr(run_etl, "DATA_PROCESSED", processed_dir)

    stats = run_etl.run()

    expected_products = len(pd.read_csv(REAL_PRODUCTS_CSV))
    expected_sales = len(pd.read_csv(REAL_SALES_CSV))
    assert stats["products_rows"] == expected_products
    assert stats["sales_rows"] == expected_sales

    products_out = pd.read_csv(processed_dir / "products_enriched.csv")
    assert "margin_pct" in products_out.columns
    sales_out = pd.read_csv(processed_dir / "sales_enriched.csv")
    assert "year_month" in sales_out.columns
