import secrets
from decimal import Decimal

from django.conf import settings
from django.core.validators import MinValueValidator, RegexValidator
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils.translation import pgettext_lazy
from django_countries.fields import CountryField

from apps.core.models import TimeStampedModel

HOME_COUNTRY = "UZ"

phone_validator = RegexValidator(
    r"^\+?[0-9 ()-]{7,20}$", _("Enter a phone number in international format.")
)


class DeliveryMethod(models.Model):
    """Способ доставки. Редактируется в админке: названия, цена, порядок."""

    class Scope(models.TextChoices):
        PICKUP = "pickup", _("Pickup")
        DOMESTIC = "domestic", _("Within Uzbekistan")
        INTERNATIONAL = "international", _("International")

    code = models.SlugField(_("code"), max_length=50, unique=True)
    name = models.CharField(_("name"), max_length=120)
    description = models.CharField(_("description"), max_length=255, blank=True)
    scope = models.CharField(_("scope"), max_length=16, choices=Scope.choices)
    price = models.DecimalField(
        _("price, USD"),
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(Decimal("0"))],
        help_text=_("Leave empty if the cost is calculated by a manager."),
    )
    is_active = models.BooleanField(_("active"), default=True)
    position = models.PositiveIntegerField(_("position"), default=0, db_index=True)

    class Meta:
        verbose_name = _("delivery method")
        verbose_name_plural = _("delivery methods")
        ordering = ["position", "id"]

    def __str__(self) -> str:
        return self.name

    def is_available_for(self, country: str) -> bool:
        """Самовывоз и доставка по стране — только для Узбекистана, BTS за рубеж — для остальных."""
        if self.scope == self.Scope.INTERNATIONAL:
            return country != HOME_COUNTRY
        return country == HOME_COUNTRY


def generate_token() -> str:
    return secrets.token_urlsafe(24)


class Order(TimeStampedModel):
    class Status(models.TextChoices):
        # Контекст перевода: «New» у статуса заказа ≠ «New» у состояния часов
        NEW = "new", pgettext_lazy("order status", "New")
        CONFIRMED = "confirmed", pgettext_lazy("order status", "Confirmed")
        PAID = "paid", pgettext_lazy("order status", "Paid")
        SHIPPED = "shipped", pgettext_lazy("order status", "Shipped")
        COMPLETED = "completed", pgettext_lazy("order status", "Completed")
        CANCELLED = "cancelled", pgettext_lazy("order status", "Cancelled")

    class ContactMethod(models.TextChoices):
        TELEGRAM = "telegram", "Telegram"
        WHATSAPP = "whatsapp", "WhatsApp"
        PHONE = "phone", _("Phone call")

    # Разрешённые переходы статусов: отменить можно до отправки
    TRANSITIONS: dict[str, set[str]] = {
        Status.NEW: {Status.CONFIRMED, Status.CANCELLED},
        Status.CONFIRMED: {Status.PAID, Status.CANCELLED},
        Status.PAID: {Status.SHIPPED, Status.CANCELLED},
        Status.SHIPPED: {Status.COMPLETED},
        Status.COMPLETED: set(),
        Status.CANCELLED: set(),
    }

    number = models.CharField(_("number"), max_length=20, unique=True, editable=False)
    # Секрет для ссылки на статус заказа — без регистрации покупателя
    token = models.CharField(max_length=64, unique=True, default=generate_token, editable=False)
    status = models.CharField(
        _("status"), max_length=16, choices=Status.choices, default=Status.NEW, db_index=True
    )

    customer_name = models.CharField(_("name"), max_length=150)
    phone = models.CharField(_("phone"), max_length=32, validators=[phone_validator])
    email = models.EmailField(_("email"), blank=True)
    contact_method = models.CharField(
        _("preferred contact"), max_length=16, choices=ContactMethod.choices
    )
    country = CountryField(_("country"))
    city = models.CharField(_("city"), max_length=120)
    address = models.CharField(_("address"), max_length=255, blank=True)
    comment = models.TextField(_("comment"), blank=True)

    delivery_method = models.ForeignKey(
        DeliveryMethod, verbose_name=_("delivery"), on_delete=models.PROTECT, related_name="+"
    )
    # Стоимость доставки на момент заказа; пусто — рассчитывает менеджер
    delivery_price = models.DecimalField(
        _("delivery, USD"), max_digits=10, decimal_places=2, null=True, blank=True
    )
    subtotal = models.DecimalField(_("items, USD"), max_digits=12, decimal_places=2)
    total = models.DecimalField(_("total, USD"), max_digits=12, decimal_places=2)

    # Валюта, в которой покупатель видел цены, и курс на момент заказа
    currency = models.CharField(_("display currency"), max_length=3, default="USD")
    exchange_rate = models.DecimalField(
        _("exchange rate"), max_digits=18, decimal_places=6, default=Decimal(1)
    )
    language = models.CharField(_("language"), max_length=8, choices=settings.LANGUAGES)

    manager_note = models.TextField(_("manager note"), blank=True)

    class Meta:
        verbose_name = _("order")
        verbose_name_plural = _("orders")
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return self.number

    def save(self, *args, **kwargs) -> None:
        if not self.number:
            self.number = self._next_number()
        # Стоимость доставки менеджер может вписать позже — итог всегда пересчитываем
        self.total = self.subtotal + (self.delivery_price or 0)
        update_fields = kwargs.get("update_fields")
        if update_fields is not None and "delivery_price" in update_fields:
            kwargs["update_fields"] = {*update_fields, "total"}
        super().save(*args, **kwargs)

    @staticmethod
    def _next_number() -> str:
        # Короткий номер для общения с менеджером: MS-482913
        while True:
            number = f"MS-{secrets.randbelow(900000) + 100000}"
            if not Order.objects.filter(number=number).exists():
                return number

    def can_change_to(self, status: str) -> bool:
        return status in self.TRANSITIONS[self.status]

    @property
    def total_in_currency(self) -> Decimal:
        return (self.total * self.exchange_rate).quantize(Decimal("1"))


class OrderItem(models.Model):
    """Позиция заказа — снимок товара на момент покупки (товар потом могут изменить)."""

    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(
        "catalog.Product",
        verbose_name=_("product"),
        on_delete=models.SET_NULL,
        null=True,
        related_name="+",
    )
    brand = models.CharField(_("brand"), max_length=120)
    name = models.CharField(_("name"), max_length=200)
    reference = models.CharField(_("reference"), max_length=80, blank=True)
    price = models.DecimalField(_("price, USD"), max_digits=12, decimal_places=2)
    quantity = models.PositiveSmallIntegerField(_("quantity"), validators=[MinValueValidator(1)])
    # Товар был под заказ: важно для сроков и для возврата остатка при отмене
    on_order = models.BooleanField(_("on order"), default=False)
    lead_time_days = models.PositiveSmallIntegerField(_("lead time, days"), null=True, blank=True)

    class Meta:
        verbose_name = _("item")
        verbose_name_plural = _("items")

    def __str__(self) -> str:
        return f"{self.brand} {self.name} × {self.quantity}"

    @property
    def line_total(self) -> Decimal:
        return self.price * self.quantity
