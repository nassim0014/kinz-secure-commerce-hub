"""SQLAlchemy models (declarative). The current build reads from CSV
files so the dashboard is fully functional without a running Postgres.
These models are wired for the production path and are exercised by
the unit tests in tests/backend/test_models.py."""
from __future__ import annotations

from datetime import datetime

from sqlalchemy import Column, DateTime, Integer, Numeric, String
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


class ProductORM(Base):
    __tablename__ = "products"

    product_id = Column(String, primary_key=True)
    handle = Column(String, index=True)
    name = Column(String, nullable=False)
    category = Column(String, index=True)
    product_type = Column(String)
    price_tnd = Column(Numeric(10, 3), nullable=False)
    cost_tnd = Column(Numeric(10, 3), nullable=False)
    stock_units = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)


class CustomerORM(Base):
    __tablename__ = "customers"

    customer_id = Column(String, primary_key=True)
    city = Column(String, index=True)
    channel = Column(String, index=True)
    segment = Column(String)
    customer_type = Column(String)
    first_order_date = Column(DateTime)
    marketing_opt_in = Column(Integer, default=1)


class SaleORM(Base):
    __tablename__ = "sales"

    id = Column(Integer, primary_key=True, autoincrement=True)
    order_id = Column(String, index=True)
    order_date = Column(DateTime, index=True)
    customer_id = Column(String, index=True)
    customer_type = Column(String)
    channel = Column(String)
    product_id = Column(String, index=True)
    quantity = Column(Integer)
    unit_price_tnd = Column(Numeric(10, 3))
    line_total_tnd = Column(Numeric(10, 3))
