from datetime import datetime
from decimal import Decimal

from ninja import Field, Schema
from pydantic import EmailStr

from apps.orders.schemas import SUPPORTED_LANGUAGES


class AuthMethodsOut(Schema):
    telegram: bool
    sms: bool


class TelegramStartOut(Schema):
    token: str
    bot_url: str


class SmsStartIn(Schema):
    phone: str = Field(min_length=7, max_length=32)


class TokenOut(Schema):
    token: str


class VerifyIn(Schema):
    token: str = Field(max_length=64)
    code: str = Field(min_length=6, max_length=6, pattern=r"^\d{6}$")


class CustomerOut(Schema):
    phone: str
    name: str
    email: str
    telegram_username: str
    has_telegram: bool
    language: str
    currency: str
    notify_telegram: bool

    @staticmethod
    def resolve_has_telegram(obj) -> bool:
        return obj.telegram_id is not None


class CustomerUpdateIn(Schema):
    name: str | None = Field(None, max_length=150)
    email: EmailStr | None = None
    language: str | None = None
    currency: str | None = Field(None, max_length=3)
    notify_telegram: bool | None = None

    def languages_ok(self) -> bool:
        return self.language is None or self.language in SUPPORTED_LANGUAGES


class AddressIn(Schema):
    country: str = Field(min_length=2, max_length=2)
    city: str = Field(min_length=2, max_length=120)
    address: str = Field("", max_length=255)
    is_default: bool = False


class AddressOut(AddressIn):
    id: int

    @staticmethod
    def resolve_country(obj) -> str:
        return str(obj.country.code)


class OrderSummaryOut(Schema):
    number: str
    token: str
    status: str
    status_label: str
    created_at: datetime
    total: Decimal
    currency: str
    exchange_rate: Decimal
    items_count: int

    @staticmethod
    def resolve_status_label(obj) -> str:
        return obj.get_status_display()

    @staticmethod
    def resolve_items_count(obj) -> int:
        return sum(item.quantity for item in obj.items.all())
