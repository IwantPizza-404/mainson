"""Telegram Bot API: один бот Maison — уведомления менеджеру, вход и уведомления покупателей."""

import logging
from typing import Any

import httpx
from django.conf import settings

logger = logging.getLogger(__name__)


class TelegramError(Exception):
    pass


def is_configured() -> bool:
    return bool(settings.TELEGRAM_BOT_TOKEN)


def call(method: str, payload: dict[str, Any] | None = None, *, timeout: float = 10) -> Any:
    """Вызов метода Bot API. Ошибки сети и ответы ok=false → TelegramError."""
    try:
        response = httpx.post(
            f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}/{method}",
            json=payload or {},
            timeout=timeout,
        )
        data = response.json()
    except (httpx.HTTPError, ValueError) as exc:
        raise TelegramError(str(exc)) from exc
    if not data.get("ok"):
        raise TelegramError(data.get("description", "Telegram API error"))
    return data.get("result")


def url_buttons(*buttons: tuple[str, str]) -> dict:
    """Кнопки-ссылки под сообщением: (текст, url), каждая в своей строке."""
    return {"inline_keyboard": [[{"text": text, "url": url}] for text, url in buttons]}


def send_message(chat_id: int | str, text: str, *, reply_markup: dict | None = None) -> bool:
    """Отправляет HTML-сообщение. Без токена бота — пропускает (False), не падает."""
    if not is_configured() or not chat_id:
        logger.warning("Telegram bot is not configured, message skipped")
        return False
    payload: dict[str, Any] = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "HTML",
        "disable_web_page_preview": True,
    }
    if reply_markup:
        payload["reply_markup"] = reply_markup
    call("sendMessage", payload)
    return True
