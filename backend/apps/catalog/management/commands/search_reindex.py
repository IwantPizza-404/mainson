from django.core.management.base import BaseCommand, CommandError

from apps.catalog import search


class Command(BaseCommand):
    help = "Пересоздаёт поисковый индекс товаров в Meilisearch."

    def handle(self, *args, **options):
        if not search.is_enabled():
            raise CommandError("MEILISEARCH_URL не задан")
        count = search.reindex_all()
        self.stdout.write(self.style.SUCCESS(f"Проиндексировано товаров: {count}"))
