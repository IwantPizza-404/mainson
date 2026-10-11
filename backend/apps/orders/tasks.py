from celery import shared_task
from django.utils import translation

from .models import Order
from .notifications import NotificationError, format_order_message, send_telegram


@shared_task(autoretry_for=(NotificationError,), retry_backoff=30, max_retries=5)
def send_order_notification(order_id: int) -> bool:
    order = Order.objects.select_related("delivery_method").get(pk=order_id)
    # Менеджер читает по-русски, независимо от языка покупателя
    with translation.override("ru"):
        return send_telegram(format_order_message(order))
