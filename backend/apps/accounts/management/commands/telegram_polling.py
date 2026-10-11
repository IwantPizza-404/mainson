"""Бот без вебхука — для разработки: python manage.py telegram_polling"""

from django.core.management.base import BaseCommand, CommandError

from apps.accounts.bot import process_update
from apps.core import telegram


class Command(BaseCommand):
    help = "Получает сообщения боту через long polling (локальная разработка)."

    def handle(self, *args, **options):
        if not telegram.is_configured():
            raise CommandError("TELEGRAM_BOT_TOKEN не задан")
        telegram.call("deleteWebhook")
        me = telegram.call("getMe")
        self.stdout.write(
            self.style.SUCCESS(f"Бот @{me['username']} слушает сообщения. Ctrl+C — выход.")
        )
        offset = 0
        while True:
            updates = telegram.call("getUpdates", {"offset": offset, "timeout": 30}, timeout=40)
            for update in updates:
                offset = update["update_id"] + 1
                try:
                    process_update(update)
                except Exception as exc:  # одно сломанное сообщение не останавливает бота
                    self.stderr.write(f"Ошибка обработки: {exc}")
