import logging
from typing import Annotated

from django.conf import settings
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404
from django_countries import countries
from ninja import Body, Header, Router, Status
from ninja.throttling import AnonRateThrottle

from apps.core import telegram
from apps.orders.schemas import ErrorOut

from . import bot, sms
from .auth import COOKIE_NAME, current_customer, customer_auth, set_session_cookie
from .models import Address, CustomerSession, LoginRequest, hash_secret
from .schemas import (
    AddressIn,
    AddressOut,
    AuthMethodsOut,
    CustomerOut,
    CustomerUpdateIn,
    OrderSummaryOut,
    SmsStartIn,
    TelegramStartOut,
    TokenOut,
    VerifyIn,
)
from .services import LoginError, complete_login, start_sms_login

logger = logging.getLogger(__name__)

auth_router = Router(tags=["auth"])
account_router = Router(tags=["account"], auth=customer_auth)
telegram_router = Router(tags=["telegram"])


# --- Вход -------------------------------------------------------------------


@auth_router.get("/methods", response=AuthMethodsOut)
def auth_methods(request):
    return {
        "telegram": telegram.is_configured() and bool(settings.TELEGRAM_BOT_USERNAME),
        "sms": sms.is_enabled(),
    }


@auth_router.post(
    "/telegram/start",
    response={200: TelegramStartOut, 400: ErrorOut},
    throttle=[AnonRateThrottle("30/h")],
)
def telegram_start(request):
    if not settings.TELEGRAM_BOT_USERNAME:
        return Status(400, {"detail": "Telegram login is not configured."})
    _request, token = LoginRequest.create(LoginRequest.Method.TELEGRAM)
    return {"token": token, "bot_url": bot.deep_link(token)}


@auth_router.post(
    "/sms/start", response={200: TokenOut, 400: ErrorOut}, throttle=[AnonRateThrottle("5/h")]
)
def sms_start(request, payload: SmsStartIn):
    try:
        return {"token": start_sms_login(payload.phone)}
    except LoginError as exc:
        return Status(400, {"detail": str(exc)})


@auth_router.post(
    "/verify", response={200: CustomerOut, 400: ErrorOut}, throttle=[AnonRateThrottle("30/h")]
)
def verify(request: HttpRequest, response: HttpResponse, payload: VerifyIn):
    try:
        customer = complete_login(payload.token, payload.code)
    except LoginError as exc:
        return Status(400, {"detail": str(exc)})
    _session, key = CustomerSession.start(customer, request.headers.get("user-agent", ""))
    set_session_cookie(response, key)
    return customer


@auth_router.post("/logout", response={204: None})
def logout(request: HttpRequest, response: HttpResponse):
    key = request.COOKIES.get(COOKIE_NAME)
    if key:
        CustomerSession.objects.filter(key_hash=hash_secret(key)).delete()
    response.delete_cookie(COOKIE_NAME, path="/", samesite="Lax")
    return Status(204, None)


# --- Кабинет ----------------------------------------------------------------


@account_router.get("/me", response=CustomerOut)
def me(request):
    return request.auth


@account_router.patch("/me", response={200: CustomerOut, 400: ErrorOut})
def update_me(request, payload: CustomerUpdateIn):
    customer = request.auth
    if not payload.languages_ok():
        return Status(400, {"detail": "Unknown language."})
    for field, value in payload.dict(exclude_unset=True).items():
        setattr(customer, field, value if value is not None else "")
    customer.save()
    return customer


@account_router.get("/addresses", response=list[AddressOut])
def list_addresses(request):
    return request.auth.addresses.all()


@account_router.post("/addresses", response={201: AddressOut, 400: ErrorOut})
def create_address(request, payload: AddressIn):
    if payload.country.upper() not in countries:
        return Status(400, {"detail": "Unknown country."})
    customer = request.auth
    data = payload.dict()
    data["country"] = data["country"].upper()
    # Первый адрес — основной
    data["is_default"] = data["is_default"] or not customer.addresses.exists()
    return Status(201, Address.objects.create(customer=customer, **data))


@account_router.put("/addresses/{address_id}", response={200: AddressOut, 400: ErrorOut})
def update_address(request, address_id: int, payload: AddressIn):
    if payload.country.upper() not in countries:
        return Status(400, {"detail": "Unknown country."})
    address = get_object_or_404(Address, pk=address_id, customer=request.auth)
    for field, value in payload.dict().items():
        setattr(address, field, value.upper() if field == "country" else value)
    address.save()
    return address


@account_router.delete("/addresses/{address_id}", response={204: None})
def delete_address(request, address_id: int):
    get_object_or_404(Address, pk=address_id, customer=request.auth).delete()
    return Status(204, None)


@account_router.get("/orders", response=list[OrderSummaryOut])
def my_orders(request):
    return request.auth.orders.prefetch_related("items").order_by("-created_at")


# --- Вебхук Telegram ----------------------------------------------------------


@telegram_router.post("/webhook", response={200: None, 403: None})
def telegram_webhook(
    request,
    payload: Annotated[dict, Body()],
    secret: Annotated[str, Header(alias="X-Telegram-Bot-Api-Secret-Token")] = "",
):
    if not settings.TELEGRAM_WEBHOOK_SECRET or secret != settings.TELEGRAM_WEBHOOK_SECRET:
        return Status(403, None)
    try:
        bot.process_update(payload)
    except telegram.TelegramError:
        # Ответ 200 — иначе Telegram будет бесконечно повторять то же обновление
        logger.exception("Telegram update processing failed")
    return Status(200, None)


__all__ = ["account_router", "auth_router", "current_customer", "telegram_router"]
