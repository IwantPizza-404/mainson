from decimal import Decimal
from io import BytesIO

import pytest
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from PIL import Image

from apps.catalog.models import Product
from apps.catalog.tests.factories import BrandFactory, ProductFactory
from apps.content.models import HomeSection, HomeSectionItem, SiteSettings

pytestmark = pytest.mark.django_db

Kind, Source = HomeSection.Kind, HomeSection.ProductSource


@pytest.fixture(autouse=True)
def empty_home():
    # Миграция создаёт главную по умолчанию — тесты строят свою
    HomeSection.objects.all().delete()


def jpeg(size=(3000, 1200)) -> SimpleUploadedFile:
    buffer = BytesIO()
    Image.new("RGB", size, "black").save(buffer, "JPEG")
    return SimpleUploadedFile("banner.jpg", buffer.getvalue())


def home(client, lang="en") -> list[dict]:
    return client.get("/api/v1/content/home", headers={"accept-language": lang}).json()


def test_banner_image_variants(client, django_capture_on_commit_callbacks):
    with django_capture_on_commit_callbacks(execute=True):
        section = HomeSection.objects.create(kind=Kind.BANNER, image=jpeg())

    image = home(client)[0]["image"]

    assert image["srcset"].count("w,") == 2  # три варианта: 800, 1600, 2400
    assert image["url"].endswith(".webp")
    assert (image["width"], image["height"]) == (3000, 1200)
    section.refresh_from_db()
    assert not section.images_to_process()


def test_image_without_processing_falls_back_to_original(client):
    HomeSection.objects.create(kind=Kind.BANNER, image=jpeg())

    image = home(client)[0]["image"]

    assert image["srcset"] is None
    assert image["url"].endswith(".jpg")


def test_replacing_and_deleting_banner_cleans_files(django_capture_on_commit_callbacks):
    with django_capture_on_commit_callbacks(execute=True):
        item = HomeSectionItem.objects.create(
            section=HomeSection.objects.create(kind=Kind.HERO), image=jpeg()
        )
    item.refresh_from_db()
    old = item.all_stored_files()
    storage = item.image.storage

    with django_capture_on_commit_callbacks(execute=True):
        item.image = jpeg((1000, 1000))
        item.save()
    item.refresh_from_db()
    assert not any(storage.exists(p) for p in old if "variants/" in p)

    current = item.all_stored_files()
    with django_capture_on_commit_callbacks(execute=True):
        item.delete()
    assert not any(storage.exists(p) for p in current)


def test_product_sources_and_sold_out_hidden(client):
    ProductFactory(slug="new-one")
    ProductFactory(slug="sold", availability=Product.Availability.SOLD_OUT, stock_quantity=0)
    ProductFactory(slug="used", condition=Product.Condition.PRE_OWNED)
    ProductFactory(slug="sale", price=Decimal("100"), compare_at_price=Decimal("150"))
    HomeSection.objects.create(kind=Kind.PRODUCTS, product_source=Source.NEW, position=1)
    HomeSection.objects.create(kind=Kind.PRODUCTS, product_source=Source.PRE_OWNED, position=2)
    HomeSection.objects.create(kind=Kind.PRODUCTS, product_source=Source.SALE, position=3)

    new, used, sale = (sorted(p["slug"] for p in s["products"]) for s in home(client))

    assert new == ["new-one", "sale"]
    assert used == ["used"]
    assert sale == ["sale"]


def test_manual_and_brand_sources(client):
    chosen = ProductFactory(slug="chosen")
    ProductFactory(slug="other")
    rolex = BrandFactory(slug="rolex")
    ProductFactory(slug="rolex-1", brand=rolex)
    manual = HomeSection.objects.create(kind=Kind.PRODUCTS, product_source=Source.MANUAL)
    manual.products.add(chosen)
    HomeSection.objects.create(
        kind=Kind.PRODUCTS, product_source=Source.BRAND, brand=rolex, position=1
    )

    first, second = home(client)

    assert [p["slug"] for p in first["products"]] == ["chosen"]
    assert [p["slug"] for p in second["products"]] == ["rolex-1"]


def test_empty_sections_and_inactive_are_hidden(client):
    HomeSection.objects.create(kind=Kind.PRODUCTS, product_source=Source.FEATURED)
    HomeSection.objects.create(kind=Kind.BRANDS)
    HomeSection.objects.create(kind=Kind.TRUST, is_active=False)

    assert home(client) == []


def test_limit_and_translations(client):
    for i in range(5):
        ProductFactory(slug=f"w{i}")
    HomeSection.objects.create(
        kind=Kind.PRODUCTS, product_source=Source.NEW, limit=3, title_en="New", title_ru="Новинки"
    )

    assert len(home(client)[0]["products"]) == 3
    assert home(client, "ru")[0]["title"] == "Новинки"


def test_section_validation():
    with pytest.raises(ValidationError):
        HomeSection(kind=Kind.PRODUCTS).clean()
    with pytest.raises(ValidationError):
        HomeSection(kind=Kind.PRODUCTS, product_source=Source.BRAND).clean()
    with pytest.raises(ValidationError):
        HomeSection(kind=Kind.BANNER).clean()
    with pytest.raises(ValidationError):
        HomeSectionItem(link="watches").full_clean(exclude=["section"])


def test_site_settings_singleton_and_normalization(client):
    SiteSettings.objects.update_or_create(
        pk=1, defaults={"telegram_username": "@maison_uz", "whatsapp_number": "+998 (90) 123-45-67"}
    )
    settings = SiteSettings.load()
    settings.save()

    data = client.get("/api/v1/content/settings").json()

    assert SiteSettings.objects.count() == 1
    assert data["telegram_username"] == "maison_uz"
    assert data["whatsapp_number"] == "998901234567"
