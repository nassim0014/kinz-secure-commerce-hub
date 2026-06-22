"""Pydantic response models for the KINZ API."""
from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    status: Literal["ok", "degraded"] = "ok"
    service: str
    version: str
    timestamp: datetime


class Product(BaseModel):
    product_id: str
    handle: str
    name: str
    category: str
    product_type: str
    price_tnd: float
    cost_tnd: float
    margin_tnd: float
    stock_units: int
    url: str


class ProductList(BaseModel):
    total: int
    items: list[Product]


class KpiSummary(BaseModel):
    revenue_tnd: float = Field(..., description="Total revenue across all orders in the period")
    orders: int
    avg_order_value_tnd: float
    gross_margin_tnd: float
    gross_margin_pct: float
    unique_customers: int
    b2b_share_pct: float
    top_category: str


class ChannelBreakdown(BaseModel):
    channel: str
    revenue_tnd: float
    orders: int
    avg_order_value_tnd: float
    gross_margin_pct: float


class LoginRequest(BaseModel):
    email: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: Literal["bearer"] = "bearer"
    expires_in: int
