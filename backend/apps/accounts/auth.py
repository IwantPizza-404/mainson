"""Аутентификация покупателей: ключ сессии в HttpOnly-cookie.

CSRF: cookie с SameSite=Lax не уходит с POST-запросами с чужих сайтов, а API принимает
только JSON (кросс-доменный JSON без CORS невозможен) — отдельный CSRF-токен не нужен.
"""

from typing import cast

from django.conf import settings
from django.http import HttpRequest, HttpResponse
from ninja.security import APIKeyCookie

from .models import SESSION_TTL, Customer, CustomerSession

COOKIE_NAME = "maison_session"
_NOT_LOADED = object()


def set_session_cookie(response: HttpResponse, key: str) -> None:
    response.set_cookie(
        COOKIE_NAME,
        key,
        max_age=int(SESSION_TTL.total_seconds()),
        httponly=True,
        secure=settings.SESSION_COOKIE_SECURE,
        samesite="Lax",
        path="/",
    )


def current_customer(request: HttpRequest) -> Customer | None:
    """Покупатель из cookie (для эндпоинтов, где вход необязателен — например, оформление)."""
    cached = getattr(request, "_customer", _NOT_LOADED)
    if cached is not _NOT_LOADED:
        return cast(Customer | None, cached)
    customer = CustomerSession.customer_for(request.COOKIES.get(COOKIE_NAME))
    request._customer = customer  # type: ignore[attr-defined]
    return customer


class CustomerAuth(APIKeyCookie):
    param_name = COOKIE_NAME

    def __init__(self) -> None:
        super().__init__(csrf=False)

    def authenticate(self, request: HttpRequest, key: str | None) -> Customer | None:
        return current_customer(request)


customer_auth = CustomerAuth()
