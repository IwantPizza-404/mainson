"""Обработка сообщений Telegram-боту: вход на сайт по коду.

Сценарий: сайт → «Войти через Telegram» → t.me/<бот>?start=login_<токен> →
бот просит поделиться номером (один раз) → присылает 6-значный код → покупатель вводит его на сайте.
"""

import logging
from html import escape

from django.conf import settings
from django.utils import translation
from django.utils.translation import gettext as _

from apps.core import telegram

from .models import Customer, LoginRequest, normalize_phone

logger = logging.getLogger(__name__)

LOGIN_PREFIX = "login_"
SUPPORTED = {code for code, _name in settings.LANGUAGES}


def deep_link(token: str) -> str:
    return f"https://t.me/{settings.TELEGRAM_BOT_USERNAME}?start={LOGIN_PREFIX}{token}"


def process_update(update: dict) -> None:
    message = update.get("message")
    if not message or message.get("chat", {}).get("type") != "private":
        return
    sender = message.get("from") or {}
    language = (sender.get("language_code") or "ru")[:2]
    with translation.override(language if language in SUPPORTED else "ru"):
        if "contact" in message:
            handle_contact(sender, message["contact"])
        elif (message.get("text") or "").startswith("/start"):
            payload = message["text"].removeprefix("/start").strip()
            handle_start(sender, payload)
        else:
            send_welcome(sender["id"])


def handle_start(sender: dict, payload: str) -> None:
    chat_id = sender["id"]
    if not payload.startswith(LOGIN_PREFIX):
        send_welcome(chat_id)
        return
    request = LoginRequest.active(payload.removeprefix(LOGIN_PREFIX))
    if request is None or request.method != LoginRequest.Method.TELEGRAM:
        telegram.send_message(
            chat_id, _("This login link has expired. Please start again on the website.")
        )
        return

    request.telegram_id = chat_id
    request.save(update_fields=["telegram_id"])

    customer = Customer.objects.filter(telegram_id=chat_id).first()
    if customer:
        # Номер уже подтверждён раньше — сразу присылаем код
        request.phone = customer.phone
        request.save(update_fields=["phone"])
        send_code(chat_id, request)
    else:
        telegram.send_message(
            chat_id,
            _("To log in to Maison, share your phone number with the button below."),
            reply_markup={
                "keyboard": [[{"text": _("📱 Share phone number"), "request_contact": True}]],
                "resize_keyboard": True,
                "one_time_keyboard": True,
            },
        )


def handle_contact(sender: dict, contact: dict) -> None:
    chat_id = sender["id"]
    # Только свой номер: переслать чужой контакт нельзя
    if contact.get("user_id") != chat_id:
        telegram.send_message(chat_id, _("Please share your own number using the button."))
        return
    request = (
        LoginRequest.objects.filter(
            method=LoginRequest.Method.TELEGRAM, telegram_id=chat_id, used_at__isnull=True
        )
        .order_by("-created_at")
        .first()
    )
    if request is None or LoginRequest.active_by_id(request.pk) is None:
        telegram.send_message(
            chat_id, _("This login link has expired. Please start again on the website.")
        )
        return
    request.phone = normalize_phone(contact.get("phone_number", ""))
    request.save(update_fields=["phone"])
    send_code(chat_id, request)


def send_code(chat_id: int, request: LoginRequest) -> None:
    code = request.issue_code()
    telegram.send_message(
        chat_id,
        _("Your Maison login code: <b>%(code)s</b>\nDo not share it with anyone.")
        % {"code": escape(code)},
        reply_markup={"remove_keyboard": True},
    )


def send_welcome(chat_id: int) -> None:
    telegram.send_message(
        chat_id,
        _("Welcome to Maison — authentic luxury watches."),
        reply_markup=telegram.url_buttons((_("Open the website"), settings.SITE_URL)),
    )
