"""Поиск товаров через Meilisearch (опечатки, все языки). Без Meilisearch — поиск по базе."""

import logging

import meilisearch
from django.conf import settings
from django.db.models import Q

from .models import Product

logger = logging.getLogger(__name__)

INDEX = "products"
LANGS = [code for code, _name in settings.LANGUAGES]


def is_enabled() -> bool:
    return bool(settings.MEILISEARCH_URL)


def client() -> meilisearch.Client:
    return meilisearch.Client(
        settings.MEILISEARCH_URL, settings.MEILISEARCH_API_KEY or None, timeout=5
    )


def index():
    return client().index(INDEX)


def configure_index() -> None:
    client().create_index(INDEX, {"primaryKey": "id"})
    index().update_settings(
        {
            # Порядок = важность совпадения: бренд и название важнее описания
            "searchableAttributes": [
                "brand",
                "brand_aliases",
                "reference",
                *[f"name_{lang}" for lang in LANGS],
                *[f"description_{lang}" for lang in LANGS],
            ],
            "displayedAttributes": ["id"],
            "typoTolerance": {
                # Опечатка допустима уже в словах из 4 букв («rolx» → Rolex)
                "minWordSizeForTypos": {"oneTypo": 4, "twoTypos": 8},
                # Референсы ищем точно: 126710 и 126610LN — разные модели.
                # 126610LN не число (есть буквы), поэтому отключаем опечатки на всём поле
                "disableOnNumbers": True,
                "disableOnAttributes": ["reference"],
            },
        }
    )


def document(product: Product) -> dict:
    doc = {
        "id": product.pk,
        "brand": product.brand.name,
        "brand_aliases": product.brand.search_aliases,
        "reference": product.reference,
    }
    for lang in LANGS:
        doc[f"name_{lang}"] = getattr(product, f"name_{lang}") or product.name
        doc[f"description_{lang}"] = getattr(product, f"description_{lang}") or ""
    return doc


def sync_products(ids: list[int]) -> None:
    """Опубликованные товары — в индекс, остальные — из индекса."""
    if not is_enabled() or not ids:
        return
    published = list(Product.objects.published().select_related("brand").filter(pk__in=ids))
    if published:
        index().add_documents([document(p) for p in published])
    removed = set(ids) - {p.pk for p in published}
    if removed:
        index().delete_documents([str(pk) for pk in removed])


def reindex_all() -> int:
    configure_index()
    index().delete_all_documents()
    products = list(Product.objects.published().select_related("brand"))
    if products:
        index().add_documents([document(p) for p in products])
    return len(products)


def search_ids(query: str, limit: int) -> list[int]:
    """id товаров по релевантности. При недоступном Meilisearch — поиск по базе."""
    if is_enabled():
        try:
            hits = index().search(query, {"limit": limit, "attributesToRetrieve": ["id"]})["hits"]
            return [hit["id"] for hit in hits]
        except Exception:  # любая ошибка поиска не должна ломать сайт
            logger.exception("Meilisearch search failed, falling back to database")
    condition = (
        Q(brand__name__icontains=query)
        | Q(brand__search_aliases__icontains=query)
        | Q(reference__icontains=query)
    )
    for lang in LANGS:
        condition |= Q(**{f"name_{lang}__icontains": query})
    return list(
        Product.objects.published()
        .filter(condition)
        .order_by("-created_at")
        .values_list("pk", flat=True)[:limit]
    )
