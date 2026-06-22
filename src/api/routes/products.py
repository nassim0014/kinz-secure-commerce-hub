"""Products endpoints — read KINZ catalog from CSV."""
from __future__ import annotations

import csv
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, Depends, Query

from src.api.models.schemas import Product, ProductList
from src.api.security.rbac import current_user
from src.api.utils import DATA_RAW

router = APIRouter()


def _load_products() -> list[dict]:
    path = DATA_RAW / "products.csv"
    if not path.exists():
        return []
    with path.open(encoding="utf-8") as f:
        return list(csv.DictReader(f))


@router.get("", response_model=ProductList)
def list_products(
    category: Optional[str] = Query(default=None, description="Filter by category"),
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    _: dict = Depends(current_user),
) -> ProductList:
    items = _load_products()
    if category:
        items = [p for p in items if p["category"].lower() == category.lower()]
    total = len(items)
    items = items[offset : offset + limit]
    return ProductList(
        total=total,
        items=[
            Product(
                product_id=p["product_id"],
                handle=p["handle"],
                name=p["name"],
                category=p["category"],
                product_type=p["product_type"],
                price_tnd=float(p["price_tnd"]),
                cost_tnd=float(p["cost_tnd"]),
                margin_tnd=float(p["margin_tnd"]),
                stock_units=int(p["stock_units"]),
                url=p["url"],
            )
            for p in items
        ],
    )


@router.get("/{product_id}", response_model=Product)
def get_product(product_id: str, _: dict = Depends(current_user)) -> Product:
    items = _load_products()
    match = next((p for p in items if p["product_id"] == product_id), None)
    if match is None:
        from fastapi import HTTPException

        raise HTTPException(status_code=404, detail=f"Product {product_id} not found")
    return Product(
        product_id=match["product_id"],
        handle=match["handle"],
        name=match["name"],
        category=match["category"],
        product_type=match["product_type"],
        price_tnd=float(match["price_tnd"]),
        cost_tnd=float(match["cost_tnd"]),
        margin_tnd=float(match["margin_tnd"]),
        stock_units=int(match["stock_units"]),
        url=match["url"],
    )
