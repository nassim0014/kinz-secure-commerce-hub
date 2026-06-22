"""Sales endpoints — read processed sales CSV."""
from __future__ import annotations

import csv
from datetime import date
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query

from src.api.security.rbac import current_user
from src.api.utils import DATA_PROCESSED

router = APIRouter()


def _load_sales() -> list[dict]:
    path = DATA_PROCESSED / "sales_2023_2024.csv"
    if not path.exists():
        return []
    with path.open(encoding="utf-8") as f:
        return list(csv.DictReader(f))


@router.get("")
def list_sales(
    channel: Optional[str] = Query(default=None),
    category: Optional[str] = Query(default=None),
    start_date: Optional[date] = Query(default=None),
    end_date: Optional[date] = Query(default=None),
    limit: int = Query(default=100, ge=1, le=1000),
    offset: int = Query(default=0, ge=0),
    _: dict = Depends(current_user),
) -> dict:
    rows = _load_sales()
    if channel:
        rows = [r for r in rows if r["channel"].lower() == channel.lower()]
    if category:
        rows = [r for r in rows if r["category"].lower() == category.lower()]
    if start_date:
        rows = [r for r in rows if r["order_date"][:10] >= start_date.isoformat()]
    if end_date:
        rows = [r for r in rows if r["order_date"][:10] <= end_date.isoformat()]
    total = len(rows)
    rows = rows[offset : offset + limit]
    return {"total": total, "items": rows}


@router.get("/order/{order_id}")
def get_order(order_id: str, _: dict = Depends(current_user)) -> dict:
    rows = [r for r in _load_sales() if r["order_id"] == order_id]
    if not rows:
        raise HTTPException(status_code=404, detail=f"Order {order_id} not found")
    return {"order_id": order_id, "items": rows}
