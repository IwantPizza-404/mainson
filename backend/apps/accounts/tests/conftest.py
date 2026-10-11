import re

import pytest

from apps.core import telegram


class FakeTelegram:
    """Записывает сообщения бота вместо отправки в Telegram."""

    def __init__(self) -> None:
        self.sent: list[dict] = []

    def send(self, chat_id, text, *, reply_markup=None):
        self.sent.append({"chat_id": chat_id, "text": text, "reply_markup": reply_markup})
        return True

    @property
    def last(self) -> dict:
        return self.sent[-1]

    def last_code(self) -> str:
        match = re.search(r"<b>(\d{6})</b>", self.last["text"])
        assert match, self.last["text"]
        return match.group(1)


@pytest.fixture
def tg(monkeypatch, settings) -> FakeTelegram:
    settings.TELEGRAM_BOT_TOKEN = "test-token"
    settings.TELEGRAM_BOT_USERNAME = "maison_test_bot"
    fake = FakeTelegram()
    monkeypatch.setattr(telegram, "send_message", fake.send)
    return fake


def start_message(user_id: int, token: str, lang: str = "ru") -> dict:
    return {
        "message": {
            "chat": {"id": user_id, "type": "private"},
            "from": {"id": user_id, "language_code": lang},
            "text": f"/start login_{token}",
        }
    }


def contact_message(user_id: int, phone: str, contact_user_id: int | None = None) -> dict:
    return {
        "message": {
            "chat": {"id": user_id, "type": "private"},
            "from": {"id": user_id, "language_code": "ru"},
            "contact": {"phone_number": phone, "user_id": contact_user_id or user_id},
        }
    }
