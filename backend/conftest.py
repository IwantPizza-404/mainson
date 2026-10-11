from decimal import Decimal

import pytest

from apps.catalog.models import Product
from apps.catalog.tests.factories import ProductFactory
from apps.orders.models import DeliveryMethod


@pytest.fixture
def watch(db) -> Product:
    return ProductFactory.create(slug="watch", price=Decimal("1000"), stock_quantity=1)


@pytest.fixture
def on_order_watch(db) -> Product:
    return ProductFactory.create(
        slug="on-order",
        price=Decimal("2000"),
        availability=Product.Availability.ON_ORDER,
        stock_quantity=0,
        lead_time_days=14,
    )


@pytest.fixture
def pickup(db) -> DeliveryMethod:
    # Способы доставки создаются миграцией
    return DeliveryMethod.objects.get(code="pickup-tashkent")
