from decimal import Decimal

import pytest

from apps.accounts.auth import COOKIE_NAME
from apps.accounts.models import Address, Customer, CustomerSession
from apps.orders.models import Order
from apps.orders.tests.helpers import order_payload

pytestmark = pytest.mark.django_db


@pytest.fixture
def customer() -> Customer:
    return Customer.objects.create(phone="+998901234567", telegram_id=111, name="Aziz")


@pytest.fixture
def auth_client(client, customer):
    _session, key = CustomerSession.start(customer)
    client.cookies[COOKIE_NAME] = key
    return client


def test_update_profile(auth_client):
    response = auth_client.patch(
        "/api/v1/account/me",
        {"name": "Азиз", "email": "aziz@mail.uz", "language": "uz", "notify_telegram": False},
        content_type="application/json",
    )

    data = response.json()
    assert (data["name"], data["language"], data["notify_telegram"]) == ("Азиз", "uz", False)
    assert (
        auth_client.patch(
            "/api/v1/account/me", {"language": "fr"}, content_type="application/json"
        ).status_code
        == 400
    )


def test_addresses_crud_and_single_default(auth_client, customer):
    first = auth_client.post(
        "/api/v1/account/addresses",
        {"country": "uz", "city": "Tashkent"},
        content_type="application/json",
    ).json()
    second = auth_client.post(
        "/api/v1/account/addresses",
        {"country": "AE", "city": "Dubai", "is_default": True},
        content_type="application/json",
    ).json()

    assert first["is_default"] is True and first["country"] == "UZ"
    assert Address.objects.get(pk=first["id"]).is_default is False
    assert second["is_default"] is True

    assert auth_client.delete(f"/api/v1/account/addresses/{first['id']}").status_code == 204
    assert [a["id"] for a in auth_client.get("/api/v1/account/addresses").json()] == [second["id"]]


def test_cannot_touch_other_customers_address(auth_client):
    other = Customer.objects.create(phone="+998900000000")
    address = Address.objects.create(customer=other, country="UZ", city="Samarkand")

    assert auth_client.delete(f"/api/v1/account/addresses/{address.pk}").status_code == 404


def test_expired_session_is_rejected(client, customer):
    session, key = CustomerSession.start(customer)
    CustomerSession.objects.filter(pk=session.pk).update(expires_at="2000-01-01T00:00Z")
    client.cookies[COOKIE_NAME] = key

    assert client.get("/api/v1/account/me").status_code == 401


def test_checkout_attaches_customer_and_saves_address(auth_client, customer, watch, pickup):
    response = auth_client.post(
        "/api/v1/orders", order_payload(save_address=True), content_type="application/json"
    )

    order = Order.objects.get(number=response.json()["number"])
    assert order.customer == customer
    assert customer.addresses.get().city == "Tashkent"
    assert auth_client.get("/api/v1/account/orders").json()[0]["total"] == str(Decimal("1000.00"))


def test_guest_checkout_has_no_customer(client, watch, pickup):
    number = client.post("/api/v1/orders", order_payload(), content_type="application/json").json()[
        "number"
    ]

    assert Order.objects.get(number=number).customer is None
