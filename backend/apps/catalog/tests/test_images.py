from io import BytesIO

import pytest
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from PIL import Image

from apps.catalog.models import Product, ProductImage

from .factories import ProductFactory

pytestmark = pytest.mark.django_db


def make_upload(name="watch.jpg", size=(3000, 2000), fmt="JPEG", exif_orientation=None):
    image = Image.new("RGB", size, "navy")
    buffer = BytesIO()
    kwargs = {}
    if exif_orientation:
        exif = Image.Exif()
        exif[0x0112] = exif_orientation
        kwargs["exif"] = exif
    image.save(buffer, format=fmt, **kwargs)
    return SimpleUploadedFile(name, buffer.getvalue())


def size_of(field) -> tuple[int, int]:
    field.open("rb")
    with Image.open(field) as image:
        assert image.format == "WEBP"
        return image.size


@pytest.fixture
def upload(django_capture_on_commit_callbacks):
    """Создаёт фото и выполняет фоновую обработку (Celery в тестах синхронный)."""

    def _upload(**kwargs) -> ProductImage:
        with django_capture_on_commit_callbacks(execute=True):
            product: Product = ProductFactory.create()
            image = ProductImage.objects.create(product=product, image=make_upload(**kwargs))
        image.refresh_from_db()
        return image

    return _upload


def test_variants_are_created_in_webp(upload):
    image = upload()

    assert size_of(image.thumb) == (400, 267)
    assert size_of(image.medium) == (800, 533)
    assert size_of(image.large) == (1600, 1067)
    assert (image.width, image.height) == (3000, 2000)
    assert not image.needs_processing


def test_small_original_is_not_upscaled(upload):
    image = upload(size=(600, 600))

    assert size_of(image.large) == (600, 600)


def test_exif_rotation_is_applied(upload):
    # Ориентация 6 — фото с телефона, снятое вертикально
    image = upload(size=(1200, 800), exif_orientation=6)

    # Повёрнуто в вертикаль; варианты ограничены по ширине
    assert size_of(image.medium) == (800, 1200)
    assert size_of(image.thumb) == (400, 600)


def test_heic_from_iphone_is_supported(upload):
    image = upload(name="IMG_0001.HEIC", size=(1000, 1000), fmt="HEIF")

    assert size_of(image.thumb) == (400, 400)


def test_replacing_photo_rebuilds_variants_and_removes_old(
    upload, django_capture_on_commit_callbacks
):
    image = upload()
    old_thumb = image.thumb.name
    storage = image.thumb.storage

    with django_capture_on_commit_callbacks(execute=True):
        image.image = make_upload(name="new.jpg", size=(2000, 2000))
        image.save()
    image.refresh_from_db()

    assert image.thumb.name != old_thumb
    assert not storage.exists(old_thumb)
    assert size_of(image.thumb) == (400, 400)


def test_deleting_photo_removes_all_files(upload, django_capture_on_commit_callbacks):
    image = upload()
    names = [image.image.name, image.thumb.name, image.medium.name, image.large.name]
    storage = image.image.storage

    with django_capture_on_commit_callbacks(execute=True):
        image.delete()

    assert not any(storage.exists(name) for name in names)


def test_unsupported_format_is_rejected():
    image = ProductImage(product=ProductFactory(), image=make_upload(name="anim.gif", fmt="GIF"))

    with pytest.raises(ValidationError) as exc:
        image.full_clean()

    assert "image" in exc.value.message_dict


def test_api_returns_variants_and_falls_back_to_original(client):
    product = ProductFactory(slug="photo")
    # Без обработки (on_commit не выполняется) — варианты ещё не построены
    ProductImage.objects.create(product=product, image=make_upload())

    image = client.get("/api/v1/catalog/products/photo").json()["images"][0]

    assert image["thumb"] == image["url"]
    assert image["width"] == 3000


def test_api_returns_built_variants(client, upload):
    image = upload()
    image.product.slug = "built"
    image.product.save()

    data = client.get("/api/v1/catalog/products/built").json()["images"][0]

    assert data["thumb"].endswith(".webp")
    assert "-thumb" in data["thumb"] and "-large" in data["large"]
