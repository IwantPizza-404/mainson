from typing import Literal

from django.db.models import Max, Min, Prefetch
from django.shortcuts import get_object_or_404
from ninja import Query, Router
from ninja.pagination import PageNumberPagination, paginate

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


@router.get("/brands", response=list[BrandOut])
def list_brands(request):
    return Brand.objects.filter(is_active=True)


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
def get_filters(request):
    """Значения для фильтров: только то, что реально встречается у опубликованных товаров."""
    products = Product.objects.published()
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
