"""Уведомления менеджеру о заказах в Telegram."""

import logging
from html import escape

from django.conf import settings
from django.urls import reverse
from django_countries import countries

from apps.core import telegram
from apps.core.telegram import TelegramError as NotificationError  # noqa: F401 — повтор задачи

from .models import Order

logger = logging.getLogger(__name__)


def format_order_message(order: Order) -> str:
    lines = [f"🛎 <b>Новый заказ {escape(order.number)}</b>", ""]
    for item in order.items.all():
        mark = f" · под заказ {item.lead_time_days} дн." if item.on_order else ""
        lines.append(
            f"• {escape(item.brand)} {escape(item.name)}"
            f"{' (' + escape(item.reference) + ')' if item.reference else ''}"
            f" × {item.quantity} — ${item.line_total:,.0f}{mark}"
        )
    delivery = escape(str(order.delivery_method))
    if order.delivery_price is None:
        delivery += " (стоимость рассчитать)"
    total = f"${order.total:,.0f}"
    if order.currency != "USD":
        total += f" ≈ {order.total_in_currency:,.0f} {order.currency}"
    lines += [
        "",
        f"<b>Итого:</b> {total}",
        f"<b>Доставка:</b> {delivery}",
        "",
        f"<b>Клиент:</b> {escape(order.customer_name)}",
        f"<b>Телефон:</b> {escape(order.phone)} · {escape(order.get_contact_method_display())}",
        f"<b>Адрес:</b> {escape(countries.name(order.country))}, {escape(order.city)}"
        f"{', ' + escape(order.address) if order.address else ''}",
    ]
    if order.comment:
        lines.append(f"<b>Комментарий:</b> {escape(order.comment)}")
    admin_url = settings.BACKEND_URL + reverse("admin:orders_order_change", args=[order.pk])
    lines += ["", f'<a href="{admin_url}">Открыть в админке</a>']
    return "\n".join(lines)


def send_telegram(text: str) -> bool:
    """Сообщение менеджеру (в личку или группу TELEGRAM_MANAGER_CHAT_ID)."""
    return telegram.send_message(settings.TELEGRAM_MANAGER_CHAT_ID, text)
