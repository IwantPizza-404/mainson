import pytest
from django.urls import reverse

from apps.catalog.models import Product
from apps.orders.models import Order
from apps.orders.services import Customer, place_order

pytestmark = pytest.mark.django_db


@pytest.fixture
def order(watch, pickup) -> Order:
    return place_order(
        items={"watch": 1},
        customer=Customer(
            name="Aziz", phone="+998901234567", contact_method="telegram", country="UZ", city="T"
        ),
        delivery_code="pickup-tashkent",
        currency="USD",
        language="ru",
    )


@pytest.fixture
def admin_client(client, django_user_model):
    client.force_login(django_user_model.objects.create_superuser("a", "a@maison.uz", "p"))
    return client


def change(admin_client, order: Order, **data):
    url = reverse("admin:orders_order_change", args=[order.pk])
    form = {"status": order.status, "manager_note": "", "delivery_price": "", **data}
    # Инлайн позиций в форме — только для чтения, но management form обязателен
    form.update({"items-TOTAL_FORMS": "0", "items-INITIAL_FORMS": "0"})
    return admin_client.post(url, form)


def test_cancel_in_admin_returns_stock(admin_client, order, watch):
    response = change(admin_client, order, status="cancelled")

    assert response.status_code == 302
    order.refresh_from_db()
    watch.refresh_from_db()
    assert order.status == Order.Status.CANCELLED
    assert watch.availability == Product.Availability.IN_STOCK


def test_admin_offers_only_allowed_statuses(admin_client, order):
    html = admin_client.get(reverse("admin:orders_order_change", args=[order.pk])).content.decode()

    assert 'value="confirmed"' in html
    assert 'value="shipped"' not in html


def test_manager_sets_delivery_price(admin_client, order):
    change(admin_client, order, delivery_price="25")

    order.refresh_from_db()
    assert order.total == order.subtotal + 25
