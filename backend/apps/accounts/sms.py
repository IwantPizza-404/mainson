"""SMS через Eskiz.uz (вход по коду для тех, у кого нет Telegram).

Включается, если заданы ESKIZ_EMAIL и ESKIZ_PASSWORD. Тексты SMS в Eskiz проходят модерацию —
шаблон «Код для входа на maison.uz: …» нужно согласовать в личном кабинете Eskiz.
"""

import logging

import httpx
from django.conf import settings
from django.core.cache import cache

logger = logging.getLogger(__name__)

API = "https://notify.eskiz.uz/api"
TOKEN_CACHE_KEY = "eskiz:token"


class SmsError(Exception):
    pass


def is_enabled() -> bool:
    return bool(settings.ESKIZ_EMAIL and settings.ESKIZ_PASSWORD)


def _token(refresh: bool = False) -> str:
    token = None if refresh else cache.get(TOKEN_CACHE_KEY)
    if token:
        return token
    try:
        response = httpx.post(
            f"{API}/auth/login",
            data={"email": settings.ESKIZ_EMAIL, "password": settings.ESKIZ_PASSWORD},
            timeout=10,
        )
        response.raise_for_status()
        token = response.json()["data"]["token"]
    except (httpx.HTTPError, KeyError, ValueError) as exc:
        raise SmsError(f"Eskiz auth failed: {exc}") from exc
    cache.set(TOKEN_CACHE_KEY, token, 60 * 60 * 24 * 25)  # токен живёт 30 дней
    return token


def send(phone: str, text: str) -> None:
    if not is_enabled():
        raise SmsError("SMS provider is not configured")
    payload = {"mobile_phone": phone.lstrip("+"), "message": text, "from": settings.ESKIZ_SENDER}
    for attempt in range(2):
        try:
            response = httpx.post(
                f"{API}/message/sms/send",
                data=payload,
                headers={"Authorization": f"Bearer {_token(refresh=attempt > 0)}"},
                timeout=10,
            )
        except httpx.HTTPError as exc:
            raise SmsError(str(exc)) from exc
        if response.status_code == 401 and attempt == 0:
            continue  # токен истёк — получаем новый и повторяем
        if response.is_error:
            raise SmsError(f"Eskiz error {response.status_code}: {response.text[:200]}")
        return
