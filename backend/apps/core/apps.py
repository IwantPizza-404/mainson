from django.apps import AppConfig


class CoreConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.core"

    def ready(self) -> None:
        # Поддержка HEIC/HEIF — формат фото с iPhone
        from pillow_heif import register_heif_opener

        register_heif_opener()

        from . import signals  # noqa: F401
