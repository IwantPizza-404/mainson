"""Уведомления покупателям в Telegram — на языке покупателя, со ссылкой на сайт."""

from html import escape

from django.conf import settings
from django.urls import reverse
from django.utils import timezone, translation
from django.utils.translation import gettext as _

from apps.catalog.models import Product
from apps.core import telegram
from apps.orders.models import Order

from .models import Customer, StockAlert, WatchRequest, WishlistItem


def site_url(customer: Customer, path: str) -> str:
    prefix = "" if customer.language == "en" else f"/{customer.language}"
    return f"{settings.SITE_URL}{prefix}{path}"


def send(customer: Customer, text: str, button: tuple[str, str] | None = None) -> bool:
    if not customer.can_receive_telegram or customer.telegram_id is None:
        return False
    markup = telegram.url_buttons(button) if button else None
    return telegram.send_message(customer.telegram_id, text, reply_markup=markup)


def product_title(product: Product) -> str:
    return escape(f"{product.brand.name} {product.name}")


# --- Заказы -------------------------------------------------------------------


def order_status_changed(order: Order) -> bool:
    customer = order.customer
    if customer is None:
        return False
    with translation.override(customer.language):
        messages: dict[str, str] = {
            Order.Status.CONFIRMED: _(
                "Your order %(number)s is confirmed. The manager will contact you about payment."
            ),
            Order.Status.PAID: _("Payment for order %(number)s received. Thank you!"),
            Order.Status.SHIPPED: _("Your order %(number)s has been shipped."),
            Order.Status.COMPLETED: _("Order %(number)s is completed. Enjoy your watch!"),
            Order.Status.CANCELLED: _("Order %(number)s has been cancelled."),
        }
        if order.status not in messages:
            return False
        text = messages[order.status] % {"number": f"<b>{escape(order.number)}</b>"}
        if order.status == Order.Status.SHIPPED and order.tracking_number:
            text += "\n" + _("BTS tracking number: <code>%(tracking)s</code>") % {
                "tracking": escape(order.tracking_number)
            }
        return send(customer, text, (_("Open order"), site_url(customer, f"/order/{order.token}")))


# --- Товары -------------------------------------------------------------------


def product_back_in_stock(product: Product) -> int:
    """Подписки на модель — разовые: после уведомления выключаются."""
    alerts = StockAlert.objects.filter(product=product, is_active=True).select_related("customer")
    sent = 0
    for alert in alerts:
        with translation.override(alert.customer.language):
            sent += send(
                alert.customer,
                _("%(product)s is available again.")
                % {"product": f"<b>{product_title(product)}</b>"},
                (_("View watch"), site_url(alert.customer, f"/watches/{product.slug}")),
            )
    alerts.update(is_active=False, notified_at=timezone.now())
    return sent


def product_published(product: Product) -> int:
    """Подписки на бренд — постоянные: каждое новое поступление."""
    alerts = StockAlert.objects.filter(brand_id=product.brand_id, is_active=True).select_related(
        "customer"
    )
    sent = 0
    for alert in alerts:
        with translation.override(alert.customer.language):
            sent += send(
                alert.customer,
                _("New arrival from %(brand)s: %(product)s")
                % {
                    "brand": escape(product.brand.name),
                    "product": f"<b>{escape(product.name)}</b>",
                },
                (_("View watch"), site_url(alert.customer, f"/watches/{product.slug}")),
            )
    alerts.update(notified_at=timezone.now())
    return sent


def price_dropped(product: Product) -> int:
    """Избранное: уведомляем, только если цена ниже той, о которой покупатель уже знает."""
    items = WishlistItem.objects.filter(
        product=product, known_price__gt=product.price
    ).select_related("customer")
    sent = 0
    for item in items:
        with translation.override(item.customer.language):
            sent += send(
                item.customer,
                _("Price drop in your favourites: %(product)s — $%(old)s → <b>$%(new)s</b>")
                % {
                    "product": product_title(product),
                    "old": f"{item.known_price:,.0f}",
                    "new": f"{product.price:,.0f}",
                },
                (_("View watch"), site_url(item.customer, f"/watches/{product.slug}")),
            )
    items.update(known_price=product.price)
    return sent


# --- «Найдите мне часы» -----------------------------------------------------------


def watch_request_created(request: WatchRequest) -> bool:
    customer = request.customer
    admin_url = settings.BACKEND_URL + reverse(
        "admin:accounts_watchrequest_change", args=[request.pk]
    )
    lines = [
        "🔎 <b>Заявка «Найдите мне часы»</b>",
        "",
        f"<b>Часы:</b> {escape(str(request))}",
        f"<b>Состояние:</b> {escape(str(request.get_condition_display()))}",
    ]
    if request.budget:
        lines.append(f"<b>Бюджет:</b> ${request.budget:,.0f}")
    if request.comment:
        lines.append(f"<b>Комментарий:</b> {escape(request.comment)}")
    lines += [
        "",
        f"<b>Клиент:</b> {escape(customer.name or '—')} · {escape(customer.phone)}",
        "",
        f'<a href="{admin_url}">Открыть в админке</a>',
    ]
    with translation.override("ru"):
        return telegram.send_message(settings.TELEGRAM_MANAGER_CHAT_ID, "\n".join(lines))


def watch_request_updated(request: WatchRequest) -> bool:
    customer = request.customer
    with translation.override(customer.language):
        text = _("Update on your request %(watch)s: <b>%(status)s</b>") % {
            "watch": escape(str(request)),
            "status": escape(str(request.get_status_display())),
        }
        if request.reply:
            text += f"\n\n{escape(request.reply)}"
        return send(customer, text, (_("Open account"), site_url(customer, "/account/requests")))
