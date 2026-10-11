from decimal import Decimal

import httpx
import pytest

from apps.orders.notifications import format_order_message, send_telegram
from apps.orders.services import Customer, place_order

pytestmark = pytest.mark.django_db


@pytest.fixture
def order(watch, pickup):
    return place_order(
        items={"watch": 1},
        customer=Customer(
            name="Aziz <b>",
            phone="+998901234567",
            contact_method="whatsapp",
            country="UZ",
            city="Tashkent",
            comment="Позвоните после 18:00",
        ),
        delivery_code="pickup-tashkent",
        currency="USD",
        language="en",
    )


def test_message_contains_order_details_and_escapes_html(order):
    text = format_order_message(order)

    assert order.number in text
    assert "$1,000" in text
    assert "Aziz &lt;b&gt;" in text
    assert "Позвоните после 18:00" in text
    assert f"/admin/orders/order/{order.pk}/change/" in text


def test_not_configured_bot_is_skipped(settings):
    settings.TELEGRAM_BOT_TOKEN = ""

    assert send_telegram("hello") is False


def test_sends_to_telegram(settings, monkeypatch):
    settings.TELEGRAM_BOT_TOKEN = "token"
    settings.TELEGRAM_MANAGER_CHAT_ID = "42"
    sent = {}

    def fake_post(url, json, timeout):
        sent.update(url=url, **json)
        return httpx.Response(200, request=httpx.Request("POST", url))

    monkeypatch.setattr(httpx, "post", fake_post)

    assert send_telegram("hi") is True
    assert sent["chat_id"] == "42" and sent["url"].endswith("/bottoken/sendMessage")


def test_total_is_formatted_with_currency(order):
    order.currency, order.exchange_rate = "UZS", Decimal("12000")

    assert "12,000,000 UZS" in format_order_message(order)
