from decimal import Decimal
from typing import Literal

from django.db.models import Count, Max, Min, Prefetch, Q
from django.shortcuts import get_object_or_404
from ninja import Query, Router
from ninja.pagination import PageNumberPagination, paginate

from . import search
from .models import Brand, Category, Product, ProductImage, SpecOption, WatchSpecs
from .schemas import (
    BrandOut,
    CategoryOut,
    FiltersOut,
    ProductDetailOut,
    ProductFilters,
    ProductListOut,
)

router = Router(tags=["catalog"])

SORTING = {
    "newest": ("-created_at",),
    "price_asc": ("price", "-created_at"),
    "price_desc": ("-price", "-created_at"),
}


class CatalogPagination(PageNumberPagination):
    page_size = 24
    max_page_size = 96


def choices(enum) -> list[dict[str, str]]:
    return [{"value": value, "label": str(label)} for value, label in enum.choices]


def published_products():
    return (
        Product.objects.published()
        .select_related("brand", "category")
        .prefetch_related(Prefetch("images", queryset=ProductImage.objects.order_by("position")))
    )


def brands_with_counts():
    """Активные бренды с числом опубликованных товаров (бренды без товаров отфильтровываются)."""
    published = Q(
        products__is_published=True,
        products__category__is_active=True,
    )
    return (
        Brand.objects.filter(is_active=True)
        .annotate(product_count=Count("products", filter=published))
        .filter(product_count__gt=0)
    )


@router.get("/brands", response=list[BrandOut])
def list_brands(request):
    return brands_with_counts()


@router.get("/brands/{slug}", response=BrandOut)
def get_brand(request, slug: str):
    return get_object_or_404(brands_with_counts(), slug=slug)


@router.get("/categories", response=list[CategoryOut])
def list_categories(request):
    return Category.objects.filter(is_active=True).select_related("parent")


@router.get("/products", response=list[ProductListOut])
@paginate(CatalogPagination)
def list_products(
    request,
    filters: Query[ProductFilters],
    sort: Literal["newest", "price_asc", "price_desc"] = "newest",
):
    return filters.filter(published_products()).order_by(*SORTING[sort])


@router.get("/products/{slug}", response=ProductDetailOut)
def get_product(request, slug: str):
    queryset = (
        published_products()
        .select_related(
            "category__parent",
            "watch_specs__case_material",
            "watch_specs__glass",
            "watch_specs__dial_color",
            "watch_specs__strap_material",
        )
        .prefetch_related("watch_specs__complications")
    )
    return get_object_or_404(queryset, slug=slug)


@router.get("/filters", response=FiltersOut)
def get_filters(request, brand: str | None = None):
    """Значения для фильтров: только то, что реально встречается у опубликованных товаров.

    brand — для страницы бренда: варианты только по товарам этого бренда.
    """
    products = Product.objects.published()
    if brand:
        products = products.filter(brand__slug=brand)
    specs = WatchSpecs.objects.filter(product__in=products)

    def used_options(kind: SpecOption.Kind, field: str):
        ids = specs.exclude(**{f"{field}__isnull": True}).values(field)
        return SpecOption.objects.filter(kind=kind, id__in=ids)

    price = products.aggregate(min=Min("price"), max=Max("price"))

    return {
        "brands": Brand.objects.filter(id__in=products.values("brand")),
        "categories": Category.objects.filter(is_active=True).select_related("parent"),
        "conditions": choices(Product.Condition),
        "availability": choices(Product.Availability),
        "genders": choices(Product.Gender),
        "movements": choices(WatchSpecs.Movement),
        "case_materials": used_options(SpecOption.Kind.CASE_MATERIAL, "case_material"),
        "dial_colors": used_options(SpecOption.Kind.DIAL_COLOR, "dial_color"),
        "strap_materials": used_options(SpecOption.Kind.STRAP_MATERIAL, "strap_material"),
        "price": price,
    }


@router.get("/search", response=list[ProductListOut])
def search_products(request, q: str = Query(..., min_length=2, max_length=100), limit: int = 24):
    """Поиск с учётом опечаток (Meilisearch); порядок — по релевантности."""
    ids = search.search_ids(q.strip(), min(max(limit, 1), 48))
    products = published_products().in_bulk(ids)
    return [products[pk] for pk in ids if pk in products]


@router.get("/products/{slug}/related", response=list[ProductListOut])
def related_products(request, slug: str, limit: int = 8):
    """Похожие: сначала тот же бренд, затем та же категория в близком ценовом диапазоне."""
    product = get_object_or_404(Product.objects.published(), slug=slug)
    available = (
        published_products()
        .exclude(pk=product.pk)
        .exclude(availability=Product.Availability.SOLD_OUT)
    )
    limit = min(max(limit, 1), 12)
    same_brand = list(available.filter(brand_id=product.brand_id).order_by("-created_at")[:limit])
    if len(same_brand) >= limit:
        return same_brand
    similar_price = available.filter(
        category_id=product.category_id,
        price__gte=product.price * Decimal("0.6"),
        price__lte=product.price * Decimal("1.6"),
    ).exclude(pk__in=[p.pk for p in same_brand])
    return same_brand + list(similar_price.order_by("-created_at")[: limit - len(same_brand)])
