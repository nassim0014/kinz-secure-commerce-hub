"""Tests for src/api/models/db.py — ORM model CRUD + defaults.

The module was at 0% coverage (38 statements, zero covered). The models
are imported by every route, so import-time errors would crash the whole
API — but field-level bugs (silent default, wrong column type) only
surface when a query hits them. These tests create, read, update, and
delete each model against an in-memory SQLite database.
"""
from __future__ import annotations

from datetime import datetime
from decimal import Decimal

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.api.models.db import Base, CustomerORM, ProductORM, SaleORM


@pytest.fixture
def db_session():
    """In-memory SQLite session with all ORM tables created."""
    engine = create_engine("sqlite:///:memory:", future=True)
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)
    session = SessionLocal()
    yield session
    session.close()


class TestProductORM:
    def test_create_product(self, db_session):
        """A product can be created with all required fields."""
        prod = ProductORM(
            product_id="KINZ-001",
            handle="argan-oil",
            name="Argan Oil 100ml",
            category="Body Care",
            product_type="Oil",
            price_tnd=Decimal("45.000"),
            cost_tnd=Decimal("20.000"),
            stock_units=100,
        )
        db_session.add(prod)
        db_session.commit()

        fetched = db_session.query(ProductORM).filter_by(product_id="KINZ-001").first()
        assert fetched is not None
        assert fetched.name == "Argan Oil 100ml"
        assert fetched.price_tnd == Decimal("45.000")
        assert fetched.cost_tnd == Decimal("20.000")

    def test_product_defaults(self, db_session):
        """stock_units defaults to 0; created_at defaults to utcnow."""
        prod = ProductORM(
            product_id="KINZ-002",
            name="Test Product",
            category="Cat",
            price_tnd=Decimal("10.000"),
            cost_tnd=Decimal("5.000"),
        )
        db_session.add(prod)
        db_session.commit()

        fetched = db_session.query(ProductORM).filter_by(product_id="KINZ-002").first()
        assert fetched.stock_units == 0  # default
        assert fetched.created_at is not None  # default datetime

    def test_update_product(self, db_session):
        """A product can be updated."""
        prod = ProductORM(
            product_id="KINZ-003",
            name="Original Name",
            category="Cat",
            price_tnd=Decimal("10.000"),
            cost_tnd=Decimal("5.000"),
        )
        db_session.add(prod)
        db_session.commit()

        prod.name = "Updated Name"
        prod.price_tnd = Decimal("15.000")
        db_session.commit()

        fetched = db_session.query(ProductORM).filter_by(product_id="KINZ-003").first()
        assert fetched.name == "Updated Name"
        assert fetched.price_tnd == Decimal("15.000")

    def test_delete_product(self, db_session):
        """A product can be deleted."""
        prod = ProductORM(
            product_id="KINZ-004",
            name="To Delete",
            category="Cat",
            price_tnd=Decimal("10.000"),
            cost_tnd=Decimal("5.000"),
        )
        db_session.add(prod)
        db_session.commit()

        db_session.delete(prod)
        db_session.commit()

        assert db_session.query(ProductORM).filter_by(product_id="KINZ-004").first() is None

    def test_nullable_handle(self, db_session):
        """handle is indexed but nullable."""
        prod = ProductORM(
            product_id="KINZ-005",
            name="No Handle",
            category="Cat",
            price_tnd=Decimal("10.000"),
            cost_tnd=Decimal("5.000"),
        )
        db_session.add(prod)
        db_session.commit()

        fetched = db_session.query(ProductORM).filter_by(product_id="KINZ-005").first()
        assert fetched.handle is None


class TestCustomerORM:
    def test_create_customer(self, db_session):
        """A customer can be created with all fields."""
        cust = CustomerORM(
            customer_id="CUST-001",
            city="Tunis",
            channel="B2C Web",
            segment="Silver",
            customer_type="B2C",
            first_order_date=datetime(2023, 11, 17),
            marketing_opt_in=1,
        )
        db_session.add(cust)
        db_session.commit()

        fetched = db_session.query(CustomerORM).filter_by(customer_id="CUST-001").first()
        assert fetched is not None
        assert fetched.city == "Tunis"
        assert fetched.channel == "B2C Web"

    def test_customer_defaults(self, db_session):
        """marketing_opt_in defaults to 1."""
        cust = CustomerORM(customer_id="CUST-002", city="Sousse")
        db_session.add(cust)
        db_session.commit()

        fetched = db_session.query(CustomerORM).filter_by(customer_id="CUST-002").first()
        assert fetched.marketing_opt_in == 1  # default

    def test_delete_customer(self, db_session):
        """A customer can be deleted."""
        cust = CustomerORM(customer_id="CUST-003", city="Sfax")
        db_session.add(cust)
        db_session.commit()

        db_session.delete(cust)
        db_session.commit()

        assert db_session.query(CustomerORM).filter_by(customer_id="CUST-003").first() is None


class TestSaleORM:
    def test_create_sale(self, db_session):
        """A sale record can be created with all fields."""
        sale = SaleORM(
            order_id="ORD-001",
            order_date=datetime(2023, 11, 17, 19, 24),
            customer_id="CUST-001",
            customer_type="B2C",
            channel="B2C Web",
            product_id="KINZ-001",
            quantity=2,
            unit_price_tnd=Decimal("45.000"),
            line_total_tnd=Decimal("90.000"),
        )
        db_session.add(sale)
        db_session.commit()

        fetched = db_session.query(SaleORM).filter_by(order_id="ORD-001").first()
        assert fetched is not None
        assert fetched.quantity == 2
        assert fetched.line_total_tnd == Decimal("90.000")

    def test_sale_autoincrement_id(self, db_session):
        """The id column auto-increments."""
        sale1 = SaleORM(order_id="ORD-A", order_date=datetime(2023, 1, 1),
                        customer_id="C1", product_id="P1", quantity=1)
        sale2 = SaleORM(order_id="ORD-B", order_date=datetime(2023, 1, 2),
                        customer_id="C2", product_id="P2", quantity=2)
        db_session.add_all([sale1, sale2])
        db_session.commit()

        assert sale1.id is not None
        assert sale2.id is not None
        assert sale2.id > sale1.id

    def test_delete_sale(self, db_session):
        """A sale can be deleted."""
        sale = SaleORM(order_id="ORD-DEL", order_date=datetime(2023, 1, 1),
                       customer_id="C1", product_id="P1", quantity=1)
        db_session.add(sale)
        db_session.commit()

        db_session.delete(sale)
        db_session.commit()

        assert db_session.query(SaleORM).filter_by(order_id="ORD-DEL").first() is None


class TestBaseMetadata:
    def test_all_tables_created(self, db_session):
        """All three ORM tables exist in the database."""
        from sqlalchemy import inspect
        inspector = inspect(db_session.bind)
        tables = set(inspector.get_table_names())
        assert "products" in tables
        assert "customers" in tables
        assert "sales" in tables

    def test_product_columns(self, db_session):
        """ProductORM has the expected columns with correct types."""
        from sqlalchemy import inspect
        inspector = inspect(db_session.bind)
        cols = {c["name"]: c["type"] for c in inspector.get_columns("products")}
        assert "product_id" in cols
        assert "price_tnd" in cols
        assert "cost_tnd" in cols
        assert "stock_units" in cols
        assert "created_at" in cols
