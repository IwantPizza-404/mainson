from django.core.management.base import BaseCommand

from apps.catalog.models import ProductImage


class Command(BaseCommand):
    help = "Создаёт WebP-варианты фото товаров (по умолчанию — только необработанные)."

    def add_arguments(self, parser):
        parser.add_argument("--all", action="store_true", help="Пересоздать варианты для всех фото")

    def handle(self, *args, all: bool = False, **options):
        done = 0
        for image in ProductImage.objects.iterator():
            if all or image.needs_processing:
                image.process()
                done += 1
        self.stdout.write(self.style.SUCCESS(f"Обработано фото: {done}"))
