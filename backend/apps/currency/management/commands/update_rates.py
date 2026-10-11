from django.core.management.base import BaseCommand

from apps.currency.services import update_rates


class Command(BaseCommand):
    help = "Загружает актуальные курсы валют из ЦБ Узбекистана."

    def handle(self, *args, **options):
        updated = update_rates()
        self.stdout.write(self.style.SUCCESS(f"Курсы обновлены: {', '.join(updated)}"))
