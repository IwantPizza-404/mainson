from decimal import Decimal

import pytest
from django.core.exceptions import ValidationError
from django.db import IntegrityError

from apps.catalog.models import Product

from .factories import CategoryFactory, ProductFactory

pytestmark = pytest.mark.django_db


def test_old_price_must_be_greater_than_price():
    product = ProductFactory.build(price=Decimal("100"), compare_at_price=Decimal("90"))

    with pytest.raises(ValidationError) as exc:
        product.clean()

    assert "compare_at_price" in exc.value.message_dict


def test_old_price_enforced_by_database():
    with pytest.raises(IntegrityError):
        ProductFactory(price=Decimal("100"), compare_at_price=Decimal("100"))


def test_in_stock_requires_quantity():
    product = ProductFactory.build(availability=Product.Availability.IN_STOCK, stock_quantity=0)

    with pytest.raises(ValidationError) as exc:
        product.clean()

    assert "stock_quantity" in exc.value.message_dict


def test_on_order_requires_lead_time():
    product = ProductFactory.build(availability=Product.Availability.ON_ORDER, lead_time_days=None)

    with pytest.raises(ValidationError) as exc:
        product.clean()

    assert "lead_time_days" in exc.value.message_dict


def test_category_nesting_is_limited_to_one_level():
    root = CategoryFactory()
    child = CategoryFactory(parent=root)
    grandchild = CategoryFactory.build(parent=child)

    with pytest.raises(ValidationError):
        grandchild.clean()


def test_published_excludes_inactive_brand():
    ProductFactory(brand__is_active=False)
    visible = ProductFactory()

    assert list(Product.objects.published()) == [visible]
