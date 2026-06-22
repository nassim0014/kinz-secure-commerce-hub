"""ETL pipeline for KINZ sales data.

Stages:
  1. Extract  — read raw CSVs (Shopify-style product export + raw orders)
  2. Transform — validate schema, normalize types, derive computed fields
  3. Load     — write processed tables to data/processed/ (and optionally Postgres)

Run manually:
    python -m src.pipeline.jobs.run_etl

Run on schedule (production):
    APScheduler triggers this every night at 02:00 (see scheduler.py).
"""
from __future__ import annotations

import csv
import logging
from datetime import datetime
from pathlib import Path
from typing import Any

import pandas as pd

from src.api.utils import DATA_PROCESSED, DATA_RAW

logger = logging.getLogger("kinz.pipeline")


def extract_products() -> pd.DataFrame:
    path = DATA_RAW / "products.csv"
    if not path.exists():
        raise FileNotFoundError(f"Missing {path}")
    df = pd.read_csv(path)
    logger.info("Extracted %d products from %s", len(df), path)
    return df


def extract_sales() -> pd.DataFrame:
    """In production this would hit the Shopify API; for the demo we
    read a pre-existing processed file."""
    path = DATA_PROCESSED / "sales_2023_2024.csv"
    if not path.exists():
        raise FileNotFoundError(f"Missing {path}")
    df = pd.read_csv(path)
    logger.info("Extracted %d sales rows from %s", len(df), path)
    return df


def transform_products(df: pd.DataFrame) -> pd.DataFrame:
    """Validate and enrich the product table."""
    required = {"product_id", "name", "category", "price_tnd", "cost_tnd"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"products.csv missing columns: {missing}")

    df["price_tnd"] = pd.to_numeric(df["price_tnd"], errors="coerce")
    df["cost_tnd"] = pd.to_numeric(df["cost_tnd"], errors="coerce")
    df["stock_units"] = pd.to_numeric(df["stock_units"], errors="coerce").fillna(0).astype(int)

    # Drop rows where critical numerics failed to parse
    before = len(df)
    df = df.dropna(subset=["price_tnd", "cost_tnd"])
    if len(df) < before:
        logger.warning("Dropped %d product rows with invalid numerics", before - len(df))

    # Derived: margin percent
    df["margin_pct"] = ((df["price_tnd"] - df["cost_tnd"]) / df["price_tnd"]).round(4)
    return df


def transform_sales(df: pd.DataFrame) -> pd.DataFrame:
    """Validate and enrich the sales table."""
    df["order_date"] = pd.to_datetime(df["order_date"], errors="coerce")
    df["quantity"] = pd.to_numeric(df["quantity"], errors="coerce").fillna(0).astype(int)
    df["unit_price_tnd"] = pd.to_numeric(df["unit_price_tnd"], errors="coerce")
    df["line_total_tnd"] = pd.to_numeric(df["line_total_tnd"], errors="coerce")
    df["order_total_tnd"] = pd.to_numeric(df["order_total_tnd"], errors="coerce")

    before = len(df)
    df = df.dropna(subset=["order_date", "line_total_tnd"])
    if len(df) < before:
        logger.warning("Dropped %d sales rows with invalid dates/totals", before - len(df))

    # Derived columns
    df["year_month"] = df["order_date"].dt.strftime("%Y-%m")
    df["quarter"] = df["order_date"].dt.to_period("Q").astype(str)
    df["is_b2b"] = df["customer_type"].eq("B2B")
    return df


def load(df_products: pd.DataFrame, df_sales: pd.DataFrame) -> dict[str, Any]:
    DATA_PROCESSED.mkdir(parents=True, exist_ok=True)
    products_out = DATA_PROCESSED / "products_enriched.csv"
    sales_out = DATA_PROCESSED / "sales_enriched.csv"

    df_products.to_csv(products_out, index=False)
    df_sales.to_csv(sales_out, index=False)
    logger.info("Wrote %s (%d rows)", products_out, len(df_products))
    logger.info("Wrote %s (%d rows)", sales_out, len(df_sales))

    return {
        "products_rows": len(df_products),
        "sales_rows": len(df_sales),
        "products_path": str(products_out),
        "sales_path": str(sales_out),
        "ran_at": datetime.utcnow().isoformat(),
    }


def run() -> dict[str, Any]:
    logger.info("ETL run starting")
    products = transform_products(extract_products())
    sales = transform_sales(extract_sales())
    stats = load(products, sales)
    logger.info("ETL run complete: %s", stats)
    return stats


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(name)s | %(message)s")
    print(run())
