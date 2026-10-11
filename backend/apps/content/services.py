from django.db.models import F, QuerySet

from apps.catalog.api import brands_with_counts, published_products
from apps.catalog.models import Brand, Product

from .models import HomeSection

Source = HomeSection.ProductSource


def section_products(section: HomeSection) -> QuerySet[Product] | list[Product]:
    """Товары для карусели: проданные не показываем — на главной только то, что можно купить."""
    queryset = published_products().exclude(availability=Product.Availability.SOLD_OUT)
    match section.product_source:
        case Source.NEW:
            queryset = queryset.filter(condition=Product.Condition.NEW).order_by("-created_at")
        case Source.FEATURED:
            queryset = queryset.filter(is_featured=True).order_by("-created_at")
        case Source.SALE:
            queryset = queryset.filter(compare_at_price__gt=F("price")).order_by("-created_at")
        case Source.PRE_OWNED:
            queryset = queryset.filter(condition=Product.Condition.PRE_OWNED).order_by(
                "-created_at"
            )
        case Source.BRAND:
            queryset = queryset.filter(brand_id=section.brand_id).order_by("-created_at")
        case Source.MANUAL:
            # Порядок как выбрал менеджер не храним — показываем новые первыми
            queryset = queryset.filter(pk__in=section.products.values("pk")).order_by("-created_at")
        case _:
            return []
    return queryset[: section.limit]


def brands_with_products() -> QuerySet[Brand]:
    return brands_with_counts()
