"""KPI endpoints — pre-computed business metrics for the dashboard."""
from __future__ import annotations

import csv
from collections import defaultdict
from datetime import date
from typing import Optional

from fastapi import APIRouter, Depends, Query

from src.api.models.schemas import ChannelBreakdown, KpiSummary
from src.api.security.rbac import current_user
from src.api.utils import DATA_PROCESSED

router = APIRouter()


def _load_sales() -> list[dict]:
    path = DATA_PROCESSED / "sales_2023_2024.csv"
    if not path.exists():
        return []
    with path.open(encoding="utf-8") as f:
        return list(csv.DictReader(f))


@router.get("/summary", response_model=KpiSummary)
def summary(
    start_date: Optional[date] = Query(default=None),
    end_date: Optional[date] = Query(default=None),
    _: dict = Depends(current_user),
) -> KpiSummary:
    rows = _load_sales()
    if start_date:
        rows = [r for r in rows if r["order_date"][:10] >= start_date.isoformat()]
    if end_date:
        rows = [r for r in rows if r["order_date"][:10] <= end_date.isoformat()]

    if not rows:
        return KpiSummary(
            revenue_tnd=0,
            orders=0,
            avg_order_value_tnd=0,
            gross_margin_tnd=0,
            gross_margin_pct=0,
            unique_customers=0,
            b2b_share_pct=0,
            top_category="—",
        )

    order_totals: dict[str, float] = defaultdict(float)
    customers: set[str] = set()
    b2b_orders: set[str] = set()
    all_orders: set[str] = set()
    cat_revenue: dict[str, float] = defaultdict(float)

    # Pull product costs to compute gross margin per line
    product_cost: dict[str, float] = {}
    products_path = DATA_PROCESSED.parent / "raw" / "products.csv"
    if products_path.exists():
        with products_path.open(encoding="utf-8") as f:
            for row in csv.DictReader(f):
                product_cost[row["product_id"]] = float(row["cost_tnd"])

    revenue = 0.0
    cogs = 0.0
    for r in rows:
        qty = int(r["quantity"])
        line_total = float(r["line_total_tnd"])
        revenue += line_total
        cogs += product_cost.get(r["product_id"], 0) * qty
        order_totals[r["order_id"]] += line_total
        customers.add(r["customer_id"])
        all_orders.add(r["order_id"])
        if r["customer_type"] == "B2B":
            b2b_orders.add(r["order_id"])
        cat_revenue[r["category"]] += line_total

    orders_count = len(all_orders)
    aov = revenue / orders_count if orders_count else 0
    gross_margin = revenue - cogs
    gross_margin_pct = (gross_margin / revenue * 100) if revenue else 0
    b2b_share_pct = (len(b2b_orders) / orders_count * 100) if orders_count else 0
    top_category = max(cat_revenue, key=cat_revenue.get) if cat_revenue else "—"

    return KpiSummary(
        revenue_tnd=round(revenue, 3),
        orders=orders_count,
        avg_order_value_tnd=round(aov, 3),
        gross_margin_tnd=round(gross_margin, 3),
        gross_margin_pct=round(gross_margin_pct, 2),
        unique_customers=len(customers),
        b2b_share_pct=round(b2b_share_pct, 2),
        top_category=top_category,
    )


@router.get("/channels", response_model=list[ChannelBreakdown])
def channels(_: dict = Depends(current_user)) -> list[ChannelBreakdown]:
    rows = _load_sales()
    product_cost: dict[str, float] = {}
    products_path = DATA_PROCESSED.parent / "raw" / "products.csv"
    if products_path.exists():
        with products_path.open(encoding="utf-8") as f:
            for row in csv.DictReader(f):
                product_cost[row["product_id"]] = float(row["cost_tnd"])

    agg: dict[str, dict] = defaultdict(lambda: {"revenue": 0.0, "orders": set(), "cogs": 0.0})
    for r in rows:
        ch = r["channel"]
        agg[ch]["revenue"] += float(r["line_total_tnd"])
        agg[ch]["orders"].add(r["order_id"])
        agg[ch]["cogs"] += product_cost.get(r["product_id"], 0) * int(r["quantity"])

    out: list[ChannelBreakdown] = []
    for ch, v in agg.items():
        orders = len(v["orders"])
        revenue = v["revenue"]
        margin = revenue - v["cogs"]
        out.append(
            ChannelBreakdown(
                channel=ch,
                revenue_tnd=round(revenue, 3),
                orders=orders,
                avg_order_value_tnd=round(revenue / orders, 3) if orders else 0,
                gross_margin_pct=round(margin / revenue * 100, 2) if revenue else 0,
            )
        )
    out.sort(key=lambda x: x.revenue_tnd, reverse=True)
    return out
