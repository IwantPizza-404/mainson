import pytest
from django.core.cache import cache

from apps.orders.models import Order

from .helpers import order_payload

pytestmark = pytest.mark.django_db


@pytest.fixture(autouse=True)
def reset_throttle():
    cache.clear()


def post(client, payload, **headers):
    return client.post("/api/v1/orders", payload, content_type="application/json", headers=headers)


def test_quote_returns_current_prices(client, watch):
    response = client.post(
        "/api/v1/cart/quote",
        {"items": [{"slug": "watch", "quantity": 1}, {"slug": "gone", "quantity": 1}]},
        content_type="application/json",
    )

    data = response.json()
    assert data["subtotal"] == "1000.00"
    assert not data["is_valid"]
    assert data["lines"][1]["error"]


def test_create_order(client, watch, pickup, django_capture_on_commit_callbacks):
    with django_capture_on_commit_callbacks(execute=True):
        response = post(client, order_payload(), **{"accept-language": "ru"})

    assert response.status_code == 201
    data = response.json()
    order = Order.objects.get(number=data["number"])
    assert order.language == "ru"
    assert order.phone == "+998 90 123 45 67"
    assert data["status_label"] == "Новый"


def test_order_status_by_token(client, watch, pickup):
    token = post(client, order_payload()).json()["token"]

    assert client.get(f"/api/v1/orders/{token}").json()["status"] == "new"
    assert client.get("/api/v1/orders/wrong-token").status_code == 404


def test_honeypot_blocks_bots(client, watch, pickup):
    response = post(client, order_payload(website="http://spam"))

    assert response.status_code == 400
    assert not Order.objects.exists()


def test_invalid_phone_and_country(client, watch, pickup):
    assert post(client, order_payload(phone="call me")).status_code == 422
    assert post(client, order_payload(country="XX")).status_code == 400


def test_sold_out_returns_readable_error(client, watch, pickup):
    post(client, order_payload())

    response = post(client, order_payload())

    assert response.status_code == 400
    assert response.json()["detail"]


def test_order_creation_is_throttled(client, watch, pickup):
    statuses = [post(client, order_payload(items=[])).status_code for _ in range(11)]

    assert statuses[-1] == 429
