from decimal import Decimal

import pytest

from apps.catalog import search
from apps.catalog.models import Product

from .factories import BrandFactory, CategoryFactory, ProductFactory

pytestmark = pytest.mark.django_db


def names(response) -> list[str]:
    return [p["name"] for p in response.json()]


def test_database_fallback_searches_brand_aliases_and_reference(client):
    omega = BrandFactory(name="Omega", slug="omega", search_aliases="омега")
    ProductFactory(brand=omega, name_en="Speedmaster", reference="310.30")
    ProductFactory(name_en="Other")

    assert names(client.get("/api/v1/catalog/search", {"q": "омега"})) == ["Speedmaster"]
    assert names(client.get("/api/v1/catalog/search", {"q": "310.30"})) == ["Speedmaster"]
    assert client.get("/api/v1/catalog/search", {"q": "x"}).status_code == 422


def test_search_keeps_meilisearch_order_and_hides_unpublished(client, settings, monkeypatch):
    first, second = ProductFactory(name_en="First"), ProductFactory(name_en="Second")
    hidden = ProductFactory(is_published=False)
    settings.MEILISEARCH_URL = "http://meili"

    class FakeIndex:
        def search(self, query, params):
            return {"hits": [{"id": second.pk}, {"id": hidden.pk}, {"id": first.pk}]}

    monkeypatch.setattr(search, "index", lambda: FakeIndex())

    assert names(client.get("/api/v1/catalog/search", {"q": "watch"})) == ["Second", "First"]


def test_meilisearch_failure_falls_back_to_database(client, settings, monkeypatch):
    ProductFactory(name_en="Datejust")
    settings.MEILISEARCH_URL = "http://meili"

    def broken():
        raise ConnectionError("down")

    monkeypatch.setattr(search, "index", broken)

    assert names(client.get("/api/v1/catalog/search", {"q": "datejust"})) == ["Datejust"]


def test_sync_adds_published_and_removes_others(settings, monkeypatch):
    visible = ProductFactory(name_en="Visible", brand=BrandFactory(search_aliases="алиас"))
    draft = ProductFactory(is_published=False)
    settings.MEILISEARCH_URL = "http://meili"
    calls: dict = {}

    class FakeIndex:
        def add_documents(self, docs):
            calls["added"] = docs

        def delete_documents(self, ids):
            calls["deleted"] = ids

    monkeypatch.setattr(search, "index", lambda: FakeIndex())

    search.sync_products([visible.pk, draft.pk])

    assert [d["id"] for d in calls["added"]] == [visible.pk]
    assert calls["added"][0]["brand_aliases"] == "алиас"
    assert calls["added"][0]["name_ru"] == "Visible"  # без перевода — английское название
    assert calls["deleted"] == [str(draft.pk)]


def test_related_products(client):
    brand, category = BrandFactory(), CategoryFactory()
    product = ProductFactory(slug="main", brand=brand, category=category, price=Decimal("1000"))
    ProductFactory(slug="same-brand", brand=brand, category=category)
    ProductFactory(slug="similar-price", category=category, price=Decimal("1200"))
    ProductFactory(slug="too-expensive", category=category, price=Decimal("5000"))
    ProductFactory(
        slug="sold", brand=brand, availability=Product.Availability.SOLD_OUT, stock_quantity=0
    )

    data = client.get(f"/api/v1/catalog/products/{product.slug}/related").json()

    assert [p["slug"] for p in data] == ["same-brand", "similar-price"]
