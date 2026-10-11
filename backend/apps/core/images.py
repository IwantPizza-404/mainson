"""Обработка загруженных изображений: WebP-варианты разных размеров для витрины."""

from dataclasses import dataclass
from io import BytesIO
from pathlib import PurePosixPath

from django.core.exceptions import ValidationError
from django.core.files.base import ContentFile
from django.db.models.fields.files import FieldFile
from django.utils.translation import gettext_lazy as _
from PIL import Image, ImageOps

ALLOWED_EXTENSIONS = ["jpg", "jpeg", "png", "webp", "heic", "heif"]
MAX_UPLOAD_MB = 20


@dataclass(frozen=True)
class Variant:
    name: str
    width: int
    quality: int = 82


# Ширины под сетку каталога (400), карточку товара (800) и полноэкранный просмотр (1600)
PRODUCT_VARIANTS = (Variant("thumb", 400), Variant("medium", 800), Variant("large", 1600, 85))


def validate_image_size(file) -> None:
    if file.size > MAX_UPLOAD_MB * 1024 * 1024:
        raise ValidationError(_("Image must be smaller than %(mb)s MB.") % {"mb": MAX_UPLOAD_MB})


def open_normalized(field: FieldFile) -> Image.Image:
    """Открывает изображение с учётом поворота из EXIF (фото с телефона) в RGB."""
    field.open("rb")
    try:
        image: Image.Image = ImageOps.exif_transpose(Image.open(field))
        if image.mode not in ("RGB", "RGBA"):
            image = image.convert("RGBA" if "transparency" in image.info else "RGB")
        image.load()
        return image
    finally:
        field.close()


def render_variant(image: Image.Image, variant: Variant) -> ContentFile:
    copy = image.copy()
    # Только уменьшаем: маленький оригинал не растягиваем
    copy.thumbnail((variant.width, variant.width * 4), Image.Resampling.LANCZOS)
    buffer = BytesIO()
    copy.save(buffer, format="WEBP", quality=variant.quality, method=6)
    return ContentFile(buffer.getvalue())


def variant_filename(original_name: str, variant: Variant) -> str:
    return f"{PurePosixPath(original_name).stem}-{variant.name}.webp"
