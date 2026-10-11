import pytest
from django.core.cache import cache

from apps.orders.services import Customer, place_order

pytestmark = pytest.mark.django_db


@pytest.fixture(autouse=True)
def reset_throttle():
    cache.clear()


@pytest.fixture
def order(watch, pickup):
    return place_order(
        items={"watch": 1},
        customer=Customer(
            name="A", phone="+998 90 123-45-67", contact_method="phone", country="UZ", city="T"
        ),
        delivery_code="pickup-tashkent",
        currency="USD",
        language="ru",
    )


def lookup(client, number, phone):
    return client.post(
        "/api/v1/orders/lookup", {"number": number, "phone": phone}, content_type="application/json"
    )


@pytest.mark.parametrize("phone", ["+998901234567", "90 123 45 67", "998 (90) 123-45-67"])
def test_lookup_accepts_phone_formats(client, order, phone):
    response = lookup(client, order.number, phone)

    assert response.status_code == 200
    assert response.json()["token"] == order.token


def test_lookup_accepts_number_without_prefix(client, order):
    assert lookup(client, order.number.removeprefix("MS-").lower(), "901234567").status_code == 200


def test_wrong_phone_or_number_is_404(client, order):
    assert lookup(client, order.number, "+998 90 000 00 00").status_code == 404
    assert lookup(client, "MS-000000", "+998901234567").status_code == 404
