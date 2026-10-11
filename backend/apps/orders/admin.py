from django import forms
from django.contrib import admin, messages
from django.http import HttpRequest
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _
from modeltranslation.admin import TabbedTranslationAdmin
from unfold.admin import ModelAdmin, TabularInline
from unfold.contrib.filters.admin import ChoicesDropdownFilter, RangeDateFilter
from unfold.decorators import display

from .models import DeliveryMethod, Order, OrderItem
from .services import OrderError, change_status


def new_orders_badge(request: HttpRequest) -> int | None:
    """Счётчик новых заказов в меню админки."""
    return Order.objects.filter(status=Order.Status.NEW).count() or None


@admin.register(DeliveryMethod)
class DeliveryMethodAdmin(ModelAdmin, TabbedTranslationAdmin):
    list_display = ("name", "scope", "price_display", "is_active")
    list_filter = ("scope", "is_active")
    prepopulated_fields = {"code": ("name_en",)}
    ordering_field = "position"
    hide_ordering_field = True

    @display(description=_("price, USD"))
    def price_display(self, obj: DeliveryMethod) -> str:
        return f"${obj.price:,.2f}" if obj.price is not None else str(_("by manager"))


class OrderItemInline(TabularInline):
    model = OrderItem
    extra = 0
    can_delete = False
    fields = (
        "brand",
        "name",
        "reference",
        "price",
        "quantity",
        "on_order",
        "serial_number",
        "warranty_until",
    )
    # Серийный номер и гарантию менеджер вписывает при продаже — они видны в «Моей коллекции»
    readonly_fields = ("brand", "name", "reference", "price", "quantity", "on_order")

    def has_add_permission(self, request, obj=None) -> bool:
        return False


class OrderAdminForm(forms.ModelForm):
    class Meta:
        model = Order
        # Остальное — данные покупателя, только для чтения
        fields = ("status", "tracking_number", "manager_note", "delivery_price")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk and "status" in self.fields:
            # В списке — только текущий статус и допустимые переходы
            allowed = {self.instance.status, *Order.TRANSITIONS[self.instance.status]}
            self.fields["status"].choices = [c for c in Order.Status.choices if c[0] in allowed]


STATUS_COLORS = {
    Order.Status.NEW: "info",
    Order.Status.CONFIRMED: "primary",
    Order.Status.PAID: "success",
    Order.Status.SHIPPED: "warning",
    Order.Status.COMPLETED: "success",
    Order.Status.CANCELLED: "danger",
}


@admin.register(Order)
class OrderAdmin(ModelAdmin):
    form = OrderAdminForm
    list_display = (
        "number",
        "created_at",
        "status_badge",
        "customer_name",
        "phone",
        "country",
        "total_display",
        "delivery_method",
    )
    list_filter = (
        ("status", ChoicesDropdownFilter),
        ("created_at", RangeDateFilter),
        "delivery_method",
    )
    list_filter_submit = True
    search_fields = (
        "number",
        "customer_name",
        "phone",
        "email",
        "items__reference",
        "tracking_number",
    )
    list_select_related = ("delivery_method",)
    inlines = (OrderItemInline,)
    readonly_fields = (
        "number",
        "created_at",
        "customer",
        "customer_name",
        "phone",
        "email",
        "contact_method",
        "contact_links",
        "country",
        "city",
        "address",
        "comment",
        "delivery_method",
        "subtotal",
        "total",
        "currency_display",
        "language",
    )
    fieldsets = (
        (
            None,
            {
                "fields": (
                    ("number", "created_at"),
                    ("status", "tracking_number"),
                    "customer",
                    "manager_note",
                )
            },
        ),
        (
            _("Customer"),
            {
                "fields": (
                    ("customer_name", "contact_method"),
                    ("phone", "email"),
                    "contact_links",
                    "comment",
                )
            },
        ),
        (
            _("Delivery"),
            {"fields": (("delivery_method", "delivery_price"), ("country", "city"), "address")},
        ),
        (_("Amount"), {"fields": (("subtotal", "total"), "currency_display", "language")}),
    )

    def has_add_permission(self, request: HttpRequest) -> bool:
        # Заказы создаются только с сайта
        return False

    def has_delete_permission(self, request: HttpRequest, obj=None) -> bool:
        # Вместо удаления — отмена: так остатки корректно возвращаются на склад
        return False

    def save_model(self, request, obj: Order, form, change: bool) -> None:
        new_status = obj.status
        if change and "status" in form.changed_data:
            obj.status = form.initial["status"]
            try:
                change_status(obj, new_status)
            except OrderError as exc:
                self.message_user(request, str(exc), messages.ERROR)
                return
        super().save_model(request, obj, form, change)

    @display(description=_("status"), label=STATUS_COLORS)
    def status_badge(self, obj: Order) -> tuple[str, str]:
        return obj.status, obj.get_status_display()

    @display(description=_("total"))
    def total_display(self, obj: Order) -> str:
        return f"${obj.total:,.0f}"

    @display(description=_("display currency"))
    def currency_display(self, obj: Order) -> str:
        if obj.currency == "USD":
            return "USD"
        return f"{obj.total_in_currency:,.0f} {obj.currency} (1 USD = {obj.exchange_rate:,.2f})"

    @display(description=_("write to customer"))
    def contact_links(self, obj: Order) -> str:
        digits = "".join(ch for ch in obj.phone if ch.isdigit())
        return format_html(
            '<a href="https://wa.me/{}" target="_blank">WhatsApp</a> · <a href="tel:{}">{}</a>',
            digits,
            obj.phone,
            _("Call"),
        )
