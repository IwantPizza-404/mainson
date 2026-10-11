from celery import shared_task

from apps.catalog.models import Product
from apps.core.telegram import TelegramError
from apps.orders.models import Order

from . import notifications
from .models import WatchRequest

RETRY = {"autoretry_for": (TelegramError,), "retry_backoff": 30, "max_retries": 5}


@shared_task(**RETRY)
def notify_order_status(order_id: int) -> None:
    order = Order.objects.select_related("customer").filter(pk=order_id).first()
    if order:
        notifications.order_status_changed(order)


@shared_task(**RETRY)
def notify_product_events(product_id: int, events: list[str]) -> None:
    product = Product.objects.published().select_related("brand").filter(pk=product_id).first()
    if product is None:
        return
    if "back_in_stock" in events:
        notifications.product_back_in_stock(product)
    if "published" in events:
        notifications.product_published(product)
    if "price_dropped" in events:
        notifications.price_dropped(product)


@shared_task(**RETRY)
def notify_watch_request(request_id: int, created: bool) -> None:
    request = WatchRequest.objects.select_related("customer").filter(pk=request_id).first()
    if request is None:
        return
    if created:
        notifications.watch_request_created(request)
    else:
        notifications.watch_request_updated(request)
