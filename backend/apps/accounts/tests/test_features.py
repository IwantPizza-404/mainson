from decimal import Decimal

import pytest
from django.urls import reverse

from apps.accounts.auth import COOKIE_NAME
from apps.accounts.models import Customer, CustomerSession, StockAlert, WatchRequest, WishlistItem
from apps.catalog.models import Product
from apps.catalog.tests.factories import BrandFactory, ProductFactory
from apps.orders.models import Order
from apps.orders.services import Customer as OrderCustomer
from apps.orders.services import change_status, place_order

pytestmark = pytest.mark.django_db


@pytest.fixture
def customer() -> Customer:
    return Customer.objects.create(phone="+998901234567", telegram_id=111, language="ru")


@pytest.fixture
def auth_client(client, customer):
    _session, key = CustomerSession.start(customer)
    client.cookies[COOKIE_NAME] = key
    return client


def post(client, url, data=None):
    return client.post(url, data or {}, content_type="application/json")


# --- Избранное ---------------------------------------------------------------------


def test_wishlist_add_remove_and_merge(auth_client):
    ProductFactory(slug="a")
    ProductFactory(slug="b")
    ProductFactory(slug="draft", is_published=False)

    assert [p["slug"] for p in post(auth_client, "/api/v1/account/wishlist", {"slug": "a"}).json()] == ["a"]
    merged = post(auth_client, "/api/v1/account/wishlist/merge", {"slugs": ["a", "b", "draft", "nope"]}).json()
    assert sorted(p["slug"] for p in merged) == ["a", "b"]

    assert auth_client.delete("/api/v1/account/wishlist/a").status_code == 204
    assert [p["slug"] for p in auth_client.get("/api/v1/account/wishlist").json()] == ["b"]


def test_wishlist_requires_login(client):
    assert client.get("/api/v1/account/wishlist").status_code == 401


# --- Уведомления о товарах ------------------------------------------------------------


def test_back_in_stock_alert_fires_once(auth_client, tg, django_capture_on_commit_callbacks):
    product = ProductFactory(
        slug="sold", name_ru="Сабмаринер", availability=Product.Availability.SOLD_OUT, stock_quantity=0
    )
    assert post(auth_client, "/api/v1/account/alerts", {"product": "sold"}).status_code == 201

    with django_capture_on_commit_callbacks(execute=True):
        product.availability, product.stock_quantity = Product.Availability.IN_STOCK, 1
        product.save()

    assert "Сабмаринер" in tg.last["text"]
    assert tg.last["reply_markup"]["inline_keyboard"][0][0]["url"].endswith("/ru/watches/sold")
    assert not StockAlert.objects.get().is_active
    assert auth_client.get("/api/v1/account/alerts").json() == []


def test_brand_alert_on_new_arrival(auth_client, tg, django_capture_on_commit_callbacks):
    brand = BrandFactory(slug="rolex", name="Rolex")
    post(auth_client, "/api/v1/account/alerts", {"brand": "rolex"})

    with django_capture_on_commit_callbacks(execute=True):
        ProductFactory(brand=brand, name_ru="Daytona")
    with django_capture_on_commit_callbacks(execute=True):
        ProductFactory(brand=brand, name_ru="Explorer")

    assert ["Daytona" in m["text"] or "Explorer" in m["text"] for m in tg.sent] == [True, True]
    assert StockAlert.objects.get().is_active  # подписка на бренд постоянная


def test_alert_validation(auth_client):
    BrandFactory(slug="rolex")
    ProductFactory(slug="x")

    assert post(auth_client, "/api/v1/account/alerts", {}).status_code == 400
    assert post(auth_client, "/api/v1/account/alerts", {"product": "x", "brand": "rolex"}).status_code == 400
    first = post(auth_client, "/api/v1/account/alerts", {"brand": "rolex"}).json()
    again = post(auth_client, "/api/v1/account/alerts", {"brand": "rolex"}).json()
    assert first["id"] == again["id"]  # без дублей


def test_price_drop_only_below_known_price(customer, tg, django_capture_on_commit_callbacks):
    product = ProductFactory(price=Decimal("1000"))
    WishlistItem.objects.create(customer=customer, product=product, known_price=Decimal("1000"))

    def set_price(value):
        with django_capture_on_commit_callbacks(execute=True):
            product.price = Decimal(value)
            product.save()

    set_price("900")
    assert "$900" in tg.last["text"]
    set_price("950")  # подорожали — не пишем
    set_price("920")  # дешевле прошлого, но выше уже известной 900 — не пишем
    assert len(tg.sent) == 1
    set_price("850")
    assert len(tg.sent) == 2


def test_no_messages_when_notifications_disabled(customer, tg, django_capture_on_commit_callbacks):
    customer.notify_telegram = False
    customer.save()
    product = ProductFactory(price=Decimal("1000"))
    WishlistItem.objects.create(customer=customer, product=product, known_price=Decimal("1000"))

    with django_capture_on_commit_callbacks(execute=True):
        product.price = Decimal("500")
        product.save()

    assert tg.sent == []


def test_admin_bulk_publish_notifies_brand_subscribers(
    admin_client, customer, tg, django_capture_on_commit_callbacks
):
    brand = BrandFactory()
    StockAlert.objects.create(customer=customer, brand=brand)
    product = ProductFactory(brand=brand, is_published=False)

    with django_capture_on_commit_callbacks(execute=True):
        admin_client.post(
            reverse("admin:catalog_product_changelist"),
            {"action": "publish", "_selected_action": [product.pk]},
        )

    assert len(tg.sent) == 1


# --- Заказы -----------------------------------------------------------------------------


def make_order(customer, watch, pickup) -> Order:
    order = place_order(
        items={"watch": 1},
        customer=OrderCustomer(
            name="A", phone=customer.phone, contact_method="telegram", country="UZ", city="T"
        ),
        delivery_code="pickup-tashkent",
        currency="USD",
        language="ru",
        account=customer,
    )
    return order


def test_order_status_messages_with_tracking(customer, tg, watch, pickup, django_capture_on_commit_callbacks):
    order = make_order(customer, watch, pickup)
    tg.sent.clear()  # уведомление менеджеру о новом заказе не считаем

    with django_capture_on_commit_callbacks(execute=True):
        change_status(order, Order.Status.CONFIRMED)
        change_status(order, Order.Status.PAID)
        order.tracking_number = "BTS123456"
        order.save()
        change_status(order, Order.Status.SHIPPED)

    customer_messages = [m for m in tg.sent if m["chat_id"] == 111]
    assert len(customer_messages) == 3
    assert "BTS123456" in customer_messages[-1]["text"]
    assert f"/ru/order/{order.token}" in customer_messages[-1]["reply_markup"]["inline_keyboard"][0][0]["url"]


def test_collection_shows_completed_orders(auth_client, customer, watch, pickup, django_capture_on_commit_callbacks):
    order = make_order(customer, watch, pickup)
    assert auth_client.get("/api/v1/account/collection").json() == []

    for status in (Order.Status.CONFIRMED, Order.Status.PAID, Order.Status.SHIPPED, Order.Status.COMPLETED):
        change_status(order, status)
    order.items.update(serial_number="SN-1", warranty_until="2031-01-01")

    item = auth_client.get("/api/v1/account/collection").json()[0]
    assert (item["serial_number"], item["warranty_until"], item["product_slug"]) == ("SN-1", "2031-01-01", "watch")


# --- «Найдите мне часы» --------------------------------------------------------------------


def test_watch_request_flow(auth_client, customer, tg, settings, django_capture_on_commit_callbacks):
    settings.TELEGRAM_MANAGER_CHAT_ID = "manager"

    with django_capture_on_commit_callbacks(execute=True):
        response = post(
            auth_client,
            "/api/v1/account/requests",
            {"brand": "Patek Philippe", "reference": "5711", "budget": "90000", "comment": "Синий циферблат"},
        )
    assert response.status_code == 201
    assert tg.last["chat_id"] == "manager" and "5711" in tg.last["text"]

    request = WatchRequest.objects.get()
    with django_capture_on_commit_callbacks(execute=True):
        request.status = WatchRequest.Status.OFFERED
        request.reply = "Нашли, цена $95 000"
        request.save()

    assert tg.last["chat_id"] == 111
    assert "Нашли, цена $95 000" in tg.last["text"]
    assert auth_client.get("/api/v1/account/requests").json()[0]["status"] == "offered"


def test_watch_request_validation(auth_client):
    assert post(auth_client, "/api/v1/account/requests", {"brand": "X"}).status_code == 422
    assert post(auth_client, "/api/v1/account/requests", {"brand": "Rolex", "condition": "bad"}).status_code == 422
