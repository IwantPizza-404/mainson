"""Адаптивные изображения для любых моделей: WebP-варианты в JSON-поле рядом с оригиналом.

Использование:

    class Banner(ResponsiveImagesMixin, models.Model):
        RESPONSIVE_IMAGES = {"image": BANNER_VARIANTS}
        image = models.ImageField(...)
        image_variants = models.JSONField(default=dict, editable=False)

После сохранения фоновая задача строит варианты (см. signals.py), API отдаёт их через
`responsive_image(obj, "image")` в формате {url, srcset, width, height}.
"""

from django.db import models
from django.db.models.fields.files import FieldFile

from .images import Variant, open_normalized, render_variant, variant_filename

# Баннеры на всю ширину: телефон, планшет/ноутбук, большой экран
BANNER_VARIANTS = (Variant("sm", 800), Variant("md", 1600), Variant("lg", 2400, 85))
# Плитки и карточки: половина или треть экрана
TILE_VARIANTS = (Variant("sm", 600), Variant("md", 1200))

# Служебные ключи в JSON вариантов начинаются с «_»
SOURCE_KEY = "_source"
SIZE_KEY = "_size"


class ResponsiveImagesMixin(models.Model):
    RESPONSIVE_IMAGES: dict[str, tuple[Variant, ...]] = {}

    class Meta:
        abstract = True

    def _variants_of(self, field_name: str) -> dict:
        return getattr(self, f"{field_name}_variants") or {}

    def images_to_process(self) -> list[str]:
        """Поля, у которых оригинал изменился с момента построения вариантов."""
        result = []
        for name in self.RESPONSIVE_IMAGES:
            field: FieldFile = getattr(self, name)
            source = self._variants_of(name).get(SOURCE_KEY)
            if (field.name or None) != source:
                result.append(name)
        return result

    def stored_variant_names(self, field_name: str) -> list[str]:
        return [
            path for key, path in self._variants_of(field_name).items() if not key.startswith("_")
        ]

    def process_images(self) -> None:
        names = self.images_to_process()
        if not names:
            return
        stale: list[str] = []
        for name in names:
            field: FieldFile = getattr(self, name)
            stale += self.stored_variant_names(name)
            variants: dict = {}
            if field.name:
                source = open_normalized(field)
                variants[SIZE_KEY] = list(source.size)
                for variant in self.RESPONSIVE_IMAGES[name]:
                    path = field.storage.save(
                        f"variants/{variant_filename(field.name, variant)}",
                        render_variant(source, variant),
                    )
                    variants[variant.name] = path
            variants[SOURCE_KEY] = field.name or None
            setattr(self, f"{name}_variants", variants)
        type(self).objects.filter(pk=self.pk).update(  # type: ignore[attr-defined]
            **{f"{name}_variants": getattr(self, f"{name}_variants") for name in names}
        )
        storage = getattr(self, names[0]).storage
        for path in stale:
            storage.delete(path)

    def all_stored_files(self) -> list[str]:
        files = []
        for name in self.RESPONSIVE_IMAGES:
            field: FieldFile = getattr(self, name)
            if field.name:
                files.append(field.name)
            files += self.stored_variant_names(name)
        return files


def responsive_image(obj: ResponsiveImagesMixin, field_name: str, request=None) -> dict | None:
    """{url, srcset, width, height} для API. Пока варианты не построены — только оригинал."""
    field: FieldFile = getattr(obj, field_name)
    if not field.name:
        return None

    def absolute(url: str) -> str:
        return request.build_absolute_uri(url) if request else url

    storage = field.storage
    meta = obj._variants_of(field_name)
    variants = {k: v for k, v in meta.items() if not k.startswith("_")}
    built = meta.get(SOURCE_KEY) == field.name and bool(variants)
    widths = {v.name: v.width for v in obj.RESPONSIVE_IMAGES[field_name]}
    srcset = (
        ", ".join(f"{absolute(storage.url(path))} {widths[key]}w" for key, path in variants.items())
        if built
        else None
    )
    largest = max(variants, key=lambda k: widths[k]) if built else None
    # Размеры сохраняются при обработке — не открываем файл (на S3 это сетевой запрос)
    size = meta.get(SIZE_KEY) if built else None
    width, height = size if size else (None, None)
    return {
        "url": absolute(storage.url(variants[largest]) if largest else field.url),
        "srcset": srcset,
        "width": width,
        "height": height,
    }
