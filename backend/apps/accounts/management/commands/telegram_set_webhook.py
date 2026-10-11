"""Продакшен: python manage.py telegram_set_webhook — Telegram шлёт сообщения боту на сайт."""

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from apps.core import telegram


class Command(BaseCommand):
    help = "Регистрирует вебхук бота: {BACKEND_URL}/api/v1/telegram/webhook"

    def handle(self, *args, **options):
        if not telegram.is_configured() or not settings.TELEGRAM_WEBHOOK_SECRET:
            raise CommandError("Нужны TELEGRAM_BOT_TOKEN и TELEGRAM_WEBHOOK_SECRET")
        url = f"{settings.BACKEND_URL}/api/v1/telegram/webhook"
        telegram.call(
            "setWebhook",
            {
                "url": url,
                "secret_token": settings.TELEGRAM_WEBHOOK_SECRET,
                "allowed_updates": ["message"],
            },
        )
        self.stdout.write(self.style.SUCCESS(f"Вебхук: {url}"))
