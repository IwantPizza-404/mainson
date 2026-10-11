from decimal import Decimal

import pytest

from apps.catalog.models import Product, SpecOption

from .factories import (
    BrandFactory,
    CategoryFactory,
    ProductFactory,
    SpecOptionFactory,
    WatchSpecsFactory,
)

pytestmark = pytest.mark.django_db

URL = "/api/v1/catalog"


def slugs(response) -> list[str]:
    return [item["slug"] for item in response.json()["items"]]


def test_list_shows_only_published(client):
    ProductFactory(slug="visible")
    ProductFactory(slug="draft", is_published=False)

    response = client.get(f"{URL}/products")

    assert response.status_code == 200
    assert slugs(response) == ["visible"]
    assert response.json()["count"] == 1


def test_filter_by_brand_and_price(client):
    rolex = BrandFactory(slug="rolex")
    ProductFactory(slug="cheap", brand=rolex, price=Decimal("500"))
    ProductFactory(slug="match", brand=rolex, price=Decimal("5000"))
    ProductFactory(slug="other-brand", price=Decimal("5000"))

    response = client.get(f"{URL}/products", {"brand": "rolex", "price_min": "1000"})

    assert slugs(response) == ["match"]


def test_filter_by_category_includes_children(client):
    watches = CategoryFactory(slug="watches")
    ProductFactory(slug="in-child", category=CategoryFactory(parent=watches))
    ProductFactory(slug="elsewhere")

    response = client.get(f"{URL}/products", {"category": "watches"})

    assert slugs(response) == ["in-child"]


def test_filter_by_watch_specs(client):
    steel = SpecOptionFactory(kind=SpecOption.Kind.CASE_MATERIAL, slug="steel")
    WatchSpecsFactory(product__slug="steel-auto", case_material=steel)
    WatchSpecsFactory(product__slug="quartz", movement="quartz", case_material=steel)

    response = client.get(f"{URL}/products", {"case_material": "steel", "movement": "automatic"})

    assert slugs(response) == ["steel-auto"]


def test_sort_by_price(client):
    ProductFactory(slug="b", price=Decimal("200"))
    ProductFactory(slug="a", price=Decimal("100"))

    response = client.get(f"{URL}/products", {"sort": "price_asc"})

    assert slugs(response) == ["a", "b"]


def test_detail_hides_serial_number(client):
    WatchSpecsFactory(product__slug="pre-owned", serial_number="SECRET-123")

    response = client.get(f"{URL}/products/pre-owned")

    assert response.status_code == 200
    assert "SECRET-123" not in response.content.decode()
    assert response.json()["watch_specs"]["movement"]["value"] == "automatic"


def test_detail_of_unpublished_is_404(client):
    ProductFactory(slug="draft", is_published=False)

    assert client.get(f"{URL}/products/draft").status_code == 404


def test_detail_is_translated_by_accept_language(client):
    ProductFactory(slug="translated", name_en="Diver", name_ru="Дайвер")

    en = client.get(f"{URL}/products/translated", headers={"accept-language": "en"})
    ru = client.get(f"{URL}/products/translated", headers={"accept-language": "ru"})

    assert en.json()["name"] == "Diver"
    assert ru.json()["name"] == "Дайвер"


def test_untranslated_field_falls_back_to_english(client):
    ProductFactory(slug="fallback", name_en="Diver", name_uz="")

    response = client.get(f"{URL}/products/fallback", headers={"accept-language": "uz"})

    assert response.json()["name"] == "Diver"


def test_filters_list_only_used_options(client):
    used = SpecOptionFactory(kind=SpecOption.Kind.DIAL_COLOR, slug="black")
    SpecOptionFactory(kind=SpecOption.Kind.DIAL_COLOR, slug="unused")
    WatchSpecsFactory(product__price=Decimal("300"), dial_color=used)
    ProductFactory(price=Decimal("900"), availability=Product.Availability.IN_STOCK)

    data = client.get(f"{URL}/filters").json()

    assert [o["slug"] for o in data["dial_colors"]] == ["black"]
    assert data["price"] == {"min": "300.00", "max": "900.00"}
