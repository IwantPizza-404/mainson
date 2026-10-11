from datetime import datetime
from decimal import Decimal

from django.conf import settings
from ninja import Field, Schema
from pydantic import EmailStr, field_validator

from apps.catalog.schemas import ImageOut

from .models import Order


class CartItemIn(Schema):
    slug: str = Field(max_length=220)
    quantity: int = Field(ge=1, le=20)


class CartIn(Schema):
    items: list[CartItemIn] = Field(max_length=50)

    def as_dict(self) -> dict[str, int]:
        # Одинаковые позиции складываем
        result: dict[str, int] = {}
        for item in self.items:
            result[item.slug] = result.get(item.slug, 0) + item.quantity
        return result


class CartLineOut(Schema):
    slug: str
    quantity: int
    max_quantity: int
    error: str | None
    name: str | None
    brand: str | None
    reference: str | None
    price: Decimal | None
    compare_at_price: Decimal | None
    availability: str | None
    lead_time_days: int | None
    image: ImageOut | None
    line_total: Decimal


class QuoteOut(Schema):
    lines: list[CartLineOut]
    subtotal: Decimal
    is_valid: bool


class DeliveryMethodOut(Schema):
    code: str
    name: str
    description: str
    scope: str
    price: Decimal | None


class CountryOut(Schema):
    code: str
    name: str


class CheckoutOptionsOut(Schema):
    delivery_methods: list[DeliveryMethodOut]
    countries: list[CountryOut]
    home_country: str


class OrderIn(CartIn):
    customer_name: str = Field(min_length=2, max_length=150)
    phone: str = Field(pattern=r"^\+?[0-9 ()-]{7,20}$")
    email: EmailStr | None = None
    contact_method: Order.ContactMethod
    country: str = Field(min_length=2, max_length=2)
    city: str = Field(min_length=2, max_length=120)
    address: str = Field("", max_length=255)
    comment: str = Field("", max_length=2000)
    delivery_method: str
    currency: str = Field("USD", max_length=3)
    # Ловушка для ботов: поле скрыто на сайте, люди его не заполняют
    website: str = ""

    @field_validator("country")
    @classmethod
    def upper_country(cls, value: str) -> str:
        return value.upper()


class OrderItemOut(Schema):
    brand: str
    name: str
    reference: str
    price: Decimal
    quantity: int
    on_order: bool
    lead_time_days: int | None


class OrderOut(Schema):
    number: str
    token: str
    status: str
    status_label: str
    created_at: datetime
    items: list[OrderItemOut]
    delivery_method: str
    delivery_price: Decimal | None
    subtotal: Decimal
    total: Decimal
    currency: str
    exchange_rate: Decimal
    contact_method: str

    @staticmethod
    def resolve_status_label(obj: Order) -> str:
        return obj.get_status_display()

    @staticmethod
    def resolve_items(obj: Order) -> list:
        return list(obj.items.all())

    @staticmethod
    def resolve_delivery_method(obj: Order) -> str:
        return obj.delivery_method.name


class ErrorOut(Schema):
    detail: str


SUPPORTED_LANGUAGES = {code for code, _ in settings.LANGUAGES}


class OrderLookupIn(Schema):
    number: str = Field(min_length=4, max_length=20)
    phone: str = Field(min_length=7, max_length=32)


class OrderLookupOut(Schema):
    token: str
